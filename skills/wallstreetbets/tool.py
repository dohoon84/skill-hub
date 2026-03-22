from __future__ import annotations

import json
import logging
import re
import urllib.request
import urllib.parse
from datetime import datetime, timezone

from langchain_core.tools import tool

logger = logging.getLogger(__name__)

_REDDIT_BASE = "https://www.reddit.com"

_POSITIVE_WORDS = {
    "moon", "mooning", "bull", "bullish", "buy", "buying", "long", "calls", "pump",
    "rocket", "tendies", "yolo", "squeeze", "breakout", "rally", "green", "up",
    "gains", "profit", "win", "winner", "hold", "hodl", "diamond", "hands",
}
_NEGATIVE_WORDS = {
    "crash", "dump", "bear", "bearish", "sell", "puts", "short", "down", "red",
    "loss", "lose", "loser", "correction", "drop", "fall", "rekt", "bankrupt",
    "bubble", "overvalued", "avoid",
}


def _fetch_json(url: str) -> dict:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "OpenChiken/1.0 (research bot)", "Accept": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())


def _analyze_sentiment(text: str) -> str:
    words = set(re.findall(r"\b\w+\b", text.lower()))
    pos = len(words & _POSITIVE_WORDS)
    neg = len(words & _NEGATIVE_WORDS)
    if pos > neg:
        return "positive"
    elif neg > pos:
        return "negative"
    return "neutral"


@tool
def get_wsb_sentiment(ticker: str, subreddit: str = "wallstreetbets", limit: int = 50) -> str:
    """Analyze Reddit community sentiment for a specific stock or crypto ticker.
    Uses Reddit's public JSON API (free, no API key required).
    Args:
        ticker: Stock ticker or crypto symbol (e.g. AAPL, GME, BTC, TSLA)
        subreddit: Subreddit to search (default: wallstreetbets, options: investing, stocks, CryptoCurrency)
        limit: Number of posts to analyze (default: 50, max: 100)
    """
    try:
        limit = max(1, min(limit, 100))
        ticker = ticker.upper()

        url = f"{_REDDIT_BASE}/r/{subreddit}/search.json?q={ticker}&sort=new&limit={limit}&restrict_sr=1"
        data = _fetch_json(url)
        posts = data.get("data", {}).get("children", [])

        if not posts:
            return f"r/{subreddit}에서 '{ticker}' 관련 게시물을 찾을 수 없습니다."

        sentiments = {"positive": 0, "negative": 0, "neutral": 0}
        top_posts: list[dict] = []

        for post in posts:
            p = post.get("data", {})
            title = p.get("title", "")
            selftext = p.get("selftext", "")
            score = p.get("score", 0)
            comments = p.get("num_comments", 0)
            url_post = f"https://reddit.com{p.get('permalink', '')}"

            combined = f"{title} {selftext}"
            if ticker.lower() not in combined.lower():
                continue

            sentiment = _analyze_sentiment(combined)
            sentiments[sentiment] += 1

            if score > 10:
                top_posts.append({
                    "title": title[:80] + "..." if len(title) > 80 else title,
                    "score": score,
                    "comments": comments,
                    "sentiment": sentiment,
                    "url": url_post,
                })

        top_posts.sort(key=lambda x: x["score"], reverse=True)
        total = sum(sentiments.values())

        if total == 0:
            return f"r/{subreddit}에서 '{ticker}' 직접 언급 게시물 없음"

        pos_pct = sentiments["positive"] / total * 100
        neg_pct = sentiments["negative"] / total * 100
        neu_pct = sentiments["neutral"] / total * 100

        if pos_pct >= 60:
            overall = "강세 📈"
        elif neg_pct >= 60:
            overall = "약세 📉"
        else:
            overall = "혼조세 ↔️"

        lines = [
            f"💬 Reddit r/{subreddit} — {ticker} 감성 분석 ({total}건)",
            f"  긍정: {pos_pct:.0f}% | 부정: {neg_pct:.0f}% | 중립: {neu_pct:.0f}%",
            f"  종합 심리: {overall}",
        ]

        if top_posts:
            lines.append("\n  🔥 주요 게시물 (상위 3건)")
            for p in top_posts[:3]:
                emoji = "🟢" if p["sentiment"] == "positive" else ("🔴" if p["sentiment"] == "negative" else "⚪")
                lines.append(f"  {emoji} [{p['score']}pts] {p['title']}")

        return "\n".join(lines)
    except Exception as e:
        logger.error("get_wsb_sentiment failed: %s", e, exc_info=True)
        return f"Reddit 감성 분석 실패: {e}"


@tool
def get_wsb_trending(limit: int = 10) -> str:
    """Get currently trending tickers on Reddit WallStreetBets.
    Args:
        limit: Number of trending posts to scan (default: 10)
    """
    try:
        url = f"{_REDDIT_BASE}/r/wallstreetbets/hot.json?limit={min(limit, 25)}"
        data = _fetch_json(url)
        posts = data.get("data", {}).get("children", [])

        ticker_pattern = re.compile(r"\b([A-Z]{2,5})\b")
        ticker_counts: dict[str, int] = {}
        skip_words = {"WSB", "NYSE", "SEC", "CEO", "CFO", "EPS", "IPO", "ETF", "USD", "THE", "FOR", "AND", "ALL"}

        for post in posts:
            p = post.get("data", {})
            text = f"{p.get('title', '')} {p.get('selftext', '')}"
            tickers = ticker_pattern.findall(text)
            for t in tickers:
                if t not in skip_words:
                    ticker_counts[t] = ticker_counts.get(t, 0) + 1

        if not ticker_counts:
            return "현재 WallStreetBets 트렌딩 티커를 찾을 수 없습니다."

        sorted_tickers = sorted(ticker_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        lines = ["🔥 WallStreetBets 현재 화제 티커"]
        for i, (ticker, count) in enumerate(sorted_tickers, 1):
            lines.append(f"  {i}. {ticker} (언급 {count}회)")

        return "\n".join(lines)
    except Exception as e:
        logger.error("get_wsb_trending failed: %s", e, exc_info=True)
        return f"WallStreetBets 트렌딩 조회 실패: {e}"


def get_tools() -> list:
    return [get_wsb_sentiment, get_wsb_trending]
