from __future__ import annotations

import json
import logging
import os
import re
import urllib.parse
import urllib.request
from datetime import datetime, timezone

from langchain_core.tools import tool

logger = logging.getLogger(__name__)

_YOUTUBE_BASE = "https://www.googleapis.com/youtube/v3"


# ── 내부 헬퍼 ──────────────────────────────────────────────────────────────────

def _get_api_key() -> str:
    key = os.getenv("YOUTUBE_API_KEY", "").strip()
    if not key:
        raise ValueError(
            "YOUTUBE_API_KEY 환경변수가 설정되지 않았습니다. "
            ".env 파일에 YOUTUBE_API_KEY=<your_key> 를 추가하세요."
        )
    return key


def _fetch_json(url: str) -> dict:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "OpenChiken/1.0", "Accept": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _build_url(endpoint: str, params: dict) -> str:
    params["key"] = _get_api_key()
    query = urllib.parse.urlencode({k: v for k, v in params.items() if v is not None})
    return f"{_YOUTUBE_BASE}/{endpoint}?{query}"


def _parse_duration(iso: str) -> str:
    """ISO 8601 duration(PT1H2M3S)을 사람이 읽기 쉬운 형태로 변환합니다."""
    match = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", iso or "")
    if not match:
        return iso
    h, m, s = (int(x or 0) for x in match.groups())
    if h:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


def _format_number(n: int | str) -> str:
    """숫자를 읽기 쉬운 형태로 변환합니다 (예: 1234567 → 1,234,567)."""
    try:
        return f"{int(n):,}"
    except (ValueError, TypeError):
        return str(n)


def _format_publish_date(dt_str: str) -> str:
    """ISO 8601 날짜 문자열을 'YYYY-MM-DD' 형태로 변환합니다."""
    try:
        dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d")
    except Exception:
        return dt_str[:10] if len(dt_str) >= 10 else dt_str


def _extract_video_id(url_or_id: str) -> str:
    """URL 또는 동영상 ID에서 순수 video_id를 추출합니다."""
    patterns = [
        r"(?:v=|youtu\.be/|/embed/|/shorts/)([A-Za-z0-9_-]{11})",
    ]
    for pattern in patterns:
        match = re.search(pattern, url_or_id)
        if match:
            return match.group(1)
    return url_or_id.strip()


# ── 도구 함수 ──────────────────────────────────────────────────────────────────

@tool
def youtube_search(
    query: str,
    max_results: int = 10,
    order: str = "relevance",
    published_after: str = "",
    region_code: str = "KR",
    video_duration: str = "",
) -> str:
    """YouTube에서 동영상을 검색합니다.

    Args:
        query: 검색어 (예: '파이썬 강의', 'Python tutorial 2024')
        max_results: 반환할 결과 수 (1~50, 기본값: 10)
        order: 정렬 기준 - relevance(관련도순, 기본), date(최신순), viewCount(조회수순), rating(평점순)
        published_after: 이 날짜 이후 업로드된 영상만 검색 (ISO 8601 형식, 예: '2024-01-01T00:00:00Z')
        region_code: 지역 코드 (기본값: 'KR')
        video_duration: 영상 길이 필터 - any(전체, 기본), short(4분 미만), medium(4~20분), long(20분 초과)
    """
    try:
        max_results = max(1, min(max_results, 50))
        params: dict = {
            "part": "snippet",
            "q": query,
            "type": "video",
            "maxResults": max_results,
            "order": order,
            "regionCode": region_code,
            "relevanceLanguage": "ko" if region_code == "KR" else "en",
        }
        if published_after:
            params["publishedAfter"] = published_after
        if video_duration and video_duration != "any":
            params["videoDuration"] = video_duration

        data = _fetch_json(_build_url("search", params))
        items = data.get("items", [])

        if not items:
            return f"'{query}' 검색 결과가 없습니다."

        total = data.get("pageInfo", {}).get("totalResults", 0)
        lines = [f"🔍 YouTube 검색 결과: '{query}' (총 {_format_number(total)}건 중 {len(items)}개 표시)\n"]

        for i, item in enumerate(items, 1):
            snippet = item.get("snippet", {})
            video_id = item.get("id", {}).get("videoId", "")
            title = snippet.get("title", "(제목 없음)")
            channel = snippet.get("channelTitle", "?")
            published = _format_publish_date(snippet.get("publishedAt", ""))
            description = snippet.get("description", "")[:120].replace("\n", " ")
            url = f"https://www.youtube.com/watch?v={video_id}"

            lines.append(
                f"{i}. 📹 {title}\n"
                f"   채널: {channel} | 업로드: {published}\n"
                f"   설명: {description}{'...' if len(snippet.get('description','')) > 120 else ''}\n"
                f"   URL: {url} | ID: {video_id}"
            )

        return "\n\n".join(lines)
    except Exception as e:
        logger.error("youtube_search failed: %s", e, exc_info=True)
        return f"YouTube 검색 중 오류가 발생했습니다: {e}"


@tool
def youtube_video_info(video_id: str) -> str:
    """YouTube 동영상의 상세 정보를 조회합니다.

    Args:
        video_id: YouTube 동영상 ID 또는 URL (예: 'dQw4w9WgXcQ' 또는 'https://youtu.be/dQw4w9WgXcQ')
    """
    try:
        video_id = _extract_video_id(video_id)
        params = {
            "part": "snippet,statistics,contentDetails,status",
            "id": video_id,
        }
        data = _fetch_json(_build_url("videos", params))
        items = data.get("items", [])

        if not items:
            return f"동영상 ID '{video_id}'를 찾을 수 없습니다."

        item = items[0]
        snippet = item.get("snippet", {})
        stats = item.get("statistics", {})
        content = item.get("contentDetails", {})
        status = item.get("status", {})

        title = snippet.get("title", "(제목 없음)")
        channel_title = snippet.get("channelTitle", "?")
        channel_id = snippet.get("channelId", "")
        published = _format_publish_date(snippet.get("publishedAt", ""))
        description = snippet.get("description", "(설명 없음)")
        tags = snippet.get("tags", [])
        category_id = snippet.get("categoryId", "")

        duration = _parse_duration(content.get("duration", ""))
        definition = content.get("definition", "").upper()
        caption = "자막 있음" if content.get("caption") == "true" else "자막 없음"

        view_count = _format_number(stats.get("viewCount", 0))
        like_count = _format_number(stats.get("likeCount", 0))
        comment_count = _format_number(stats.get("commentCount", 0))
        favorite_count = _format_number(stats.get("favoriteCount", 0))

        privacy = status.get("privacyStatus", "?")
        embeddable = "임베드 가능" if status.get("embeddable") else "임베드 불가"

        tags_str = ", ".join(tags[:15])
        if len(tags) > 15:
            tags_str += f" 외 {len(tags) - 15}개"

        desc_preview = description[:500].replace("\n", " ")
        if len(description) > 500:
            desc_preview += "..."

        return (
            f"📹 동영상 상세 정보\n"
            f"{'=' * 50}\n"
            f"제목: {title}\n"
            f"채널: {channel_title} (ID: {channel_id})\n"
            f"업로드: {published} | 길이: {duration} | 화질: {definition}\n"
            f"공개 상태: {privacy} | {caption} | {embeddable}\n"
            f"\n📊 통계\n"
            f"조회수: {view_count} | 좋아요: {like_count} | 댓글: {comment_count}\n"
            f"\n🏷️ 태그: {tags_str or '없음'}\n"
            f"\n📝 설명:\n{desc_preview}\n"
            f"\n🔗 URL: https://www.youtube.com/watch?v={video_id}"
        )
    except Exception as e:
        logger.error("youtube_video_info failed: %s", e, exc_info=True)
        return f"동영상 정보 조회 중 오류가 발생했습니다: {e}"


@tool
def youtube_channel_info(channel_query: str) -> str:
    """YouTube 채널 정보를 조회합니다.

    Args:
        channel_query: 채널 ID, 핸들(@username), 또는 채널 이름 (예: '@MrBeast', 'UCX6OQ3DkcsbYNE6H8uQQuVA', '코딩하는가희')
    """
    try:
        channel_id = channel_query.strip()

        # @핸들 형태 처리
        if channel_id.startswith("@"):
            handle = channel_id.lstrip("@")
            search_params = {
                "part": "snippet",
                "q": handle,
                "type": "channel",
                "maxResults": 1,
            }
            search_data = _fetch_json(_build_url("search", search_params))
            search_items = search_data.get("items", [])
            if not search_items:
                return f"채널 '{channel_query}'을(를) 찾을 수 없습니다."
            channel_id = search_items[0]["snippet"]["channelId"]

        # 채널 ID가 UC로 시작하지 않으면 이름으로 검색
        elif not channel_id.startswith("UC"):
            search_params = {
                "part": "snippet",
                "q": channel_id,
                "type": "channel",
                "maxResults": 1,
            }
            search_data = _fetch_json(_build_url("search", search_params))
            search_items = search_data.get("items", [])
            if not search_items:
                return f"채널 '{channel_query}'을(를) 찾을 수 없습니다."
            channel_id = search_items[0]["snippet"]["channelId"]

        params = {
            "part": "snippet,statistics,contentDetails,brandingSettings",
            "id": channel_id,
        }
        data = _fetch_json(_build_url("channels", params))
        items = data.get("items", [])

        if not items:
            return f"채널 ID '{channel_id}'를 찾을 수 없습니다."

        item = items[0]
        snippet = item.get("snippet", {})
        stats = item.get("statistics", {})
        branding = item.get("brandingSettings", {}).get("channel", {})

        title = snippet.get("title", "(채널명 없음)")
        description = snippet.get("description", "(설명 없음)")[:400].replace("\n", " ")
        country = snippet.get("country", "?")
        created = _format_publish_date(snippet.get("publishedAt", ""))
        custom_url = snippet.get("customUrl", "")

        subscriber_count = stats.get("subscriberCount")
        subscriber_str = (
            f"{_format_number(subscriber_count)}명" if subscriber_count
            else "비공개"
        )
        video_count = _format_number(stats.get("videoCount", 0))
        view_count = _format_number(stats.get("viewCount", 0))

        keywords = branding.get("keywords", "")[:200]
        channel_url = f"https://www.youtube.com/channel/{channel_id}"
        if custom_url:
            channel_url = f"https://www.youtube.com/{custom_url}"

        return (
            f"📺 채널 정보\n"
            f"{'=' * 50}\n"
            f"채널명: {title}\n"
            f"채널 ID: {channel_id}\n"
            f"URL: {channel_url}\n"
            f"국가: {country} | 개설일: {created}\n"
            f"\n📊 통계\n"
            f"구독자: {subscriber_str} | 동영상: {video_count}개 | 총 조회수: {view_count}\n"
            f"\n📝 채널 소개:\n{description}{'...' if len(snippet.get('description','')) > 400 else ''}\n"
            f"\n🏷️ 키워드: {keywords or '없음'}"
        )
    except Exception as e:
        logger.error("youtube_channel_info failed: %s", e, exc_info=True)
        return f"채널 정보 조회 중 오류가 발생했습니다: {e}"


@tool
def youtube_trending(
    region_code: str = "KR",
    category_id: int = 0,
    max_results: int = 10,
) -> str:
    """지역별 YouTube 트렌딩(인기) 동영상을 조회합니다.

    Args:
        region_code: 지역 코드 (기본값: 'KR' 한국, 'US' 미국, 'JP' 일본 등)
        category_id: 카테고리 ID (0=전체, 10=음악, 15=동물, 17=스포츠, 20=게임, 22=블로그, 23=코미디, 24=엔터테인먼트, 25=뉴스, 26=정치, 28=과학기술)
        max_results: 반환할 결과 수 (1~50, 기본값: 10)
    """
    try:
        max_results = max(1, min(max_results, 50))
        params: dict = {
            "part": "snippet,statistics,contentDetails",
            "chart": "mostPopular",
            "regionCode": region_code,
            "maxResults": max_results,
        }
        if category_id:
            params["videoCategoryId"] = category_id

        _CATEGORY_NAMES = {
            0: "전체", 10: "음악", 15: "동물", 17: "스포츠", 20: "게임",
            22: "블로그/Vlog", 23: "코미디", 24: "엔터테인먼트", 25: "뉴스/정치",
            28: "과학/기술",
        }
        category_name = _CATEGORY_NAMES.get(category_id, f"카테고리 {category_id}")

        data = _fetch_json(_build_url("videos", params))
        items = data.get("items", [])

        if not items:
            return f"'{region_code}' 지역 트렌딩 동영상을 찾을 수 없습니다."

        region_flag = {
            "KR": "🇰🇷", "US": "🇺🇸", "JP": "🇯🇵", "GB": "🇬🇧",
            "DE": "🇩🇪", "FR": "🇫🇷", "IN": "🇮🇳", "BR": "🇧🇷",
        }.get(region_code, "🌍")

        lines = [f"{region_flag} YouTube 트렌딩 TOP {len(items)} — {region_code} / {category_name}\n"]

        for i, item in enumerate(items, 1):
            video_id = item.get("id", "")
            snippet = item.get("snippet", {})
            stats = item.get("statistics", {})
            content = item.get("contentDetails", {})

            title = snippet.get("title", "(제목 없음)")
            channel = snippet.get("channelTitle", "?")
            published = _format_publish_date(snippet.get("publishedAt", ""))
            duration = _parse_duration(content.get("duration", ""))
            views = _format_number(stats.get("viewCount", 0))
            likes = _format_number(stats.get("likeCount", 0))
            comments = _format_number(stats.get("commentCount", 0))
            url = f"https://www.youtube.com/watch?v={video_id}"

            lines.append(
                f"{i}. 🔥 {title}\n"
                f"   채널: {channel} | 길이: {duration} | 업로드: {published}\n"
                f"   조회수: {views} | 좋아요: {likes} | 댓글: {comments}\n"
                f"   URL: {url} | ID: {video_id}"
            )

        return "\n\n".join(lines)
    except Exception as e:
        logger.error("youtube_trending failed: %s", e, exc_info=True)
        return f"트렌딩 동영상 조회 중 오류가 발생했습니다: {e}"


@tool
def youtube_comments(
    video_id: str,
    max_results: int = 20,
    order: str = "relevance",
) -> str:
    """YouTube 동영상의 댓글을 조회합니다.

    Args:
        video_id: YouTube 동영상 ID 또는 URL
        max_results: 반환할 댓글 수 (1~100, 기본값: 20)
        order: 정렬 기준 - relevance(관련도순/인기순, 기본), time(최신순)
    """
    try:
        video_id = _extract_video_id(video_id)
        max_results = max(1, min(max_results, 100))
        params = {
            "part": "snippet",
            "videoId": video_id,
            "maxResults": max_results,
            "order": order,
            "textFormat": "plainText",
        }

        data = _fetch_json(_build_url("commentThreads", params))
        items = data.get("items", [])

        if not items:
            return f"동영상 ID '{video_id}'의 댓글을 찾을 수 없습니다. (댓글이 비활성화되어 있을 수 있습니다.)"

        total = data.get("pageInfo", {}).get("totalResults", 0)
        lines = [
            f"💬 댓글 목록 — 동영상 ID: {video_id}\n"
            f"https://www.youtube.com/watch?v={video_id}\n"
            f"총 댓글 수: {_format_number(total)}개 (상위 {len(items)}개 표시)\n"
        ]

        for i, item in enumerate(items, 1):
            top = item.get("snippet", {}).get("topLevelComment", {}).get("snippet", {})
            author = top.get("authorDisplayName", "?")
            text = top.get("textDisplay", "").replace("\n", " ")[:300]
            if len(top.get("textDisplay", "")) > 300:
                text += "..."
            likes = _format_number(top.get("likeCount", 0))
            published = _format_publish_date(top.get("publishedAt", ""))
            reply_count = item.get("snippet", {}).get("totalReplyCount", 0)

            reply_str = f" | 답글 {reply_count}개" if reply_count else ""
            lines.append(
                f"{i}. 👤 {author} ({published}) | 👍 {likes}{reply_str}\n"
                f"   {text}"
            )

        return "\n\n".join(lines)
    except Exception as e:
        logger.error("youtube_comments failed: %s", e, exc_info=True)
        return f"댓글 조회 중 오류가 발생했습니다: {e}"


@tool
def youtube_playlist_items(
    playlist_id: str,
    max_results: int = 20,
) -> str:
    """YouTube 재생목록의 동영상 목록을 조회합니다.

    Args:
        playlist_id: YouTube 재생목록 ID (예: 'PLxxxxxxxxxxxxxxxx') 또는 재생목록 URL
        max_results: 반환할 동영상 수 (1~50, 기본값: 20)
    """
    try:
        # URL에서 playlist_id 추출
        pl_match = re.search(r"list=([A-Za-z0-9_-]+)", playlist_id)
        if pl_match:
            playlist_id = pl_match.group(1)
        playlist_id = playlist_id.strip()

        max_results = max(1, min(max_results, 50))
        params = {
            "part": "snippet,contentDetails",
            "playlistId": playlist_id,
            "maxResults": max_results,
        }

        data = _fetch_json(_build_url("playlistItems", params))
        items = data.get("items", [])

        if not items:
            return f"재생목록 ID '{playlist_id}'에서 동영상을 찾을 수 없습니다."

        total = data.get("pageInfo", {}).get("totalResults", 0)
        pl_url = f"https://www.youtube.com/playlist?list={playlist_id}"
        lines = [
            f"📋 재생목록 동영상 목록\n"
            f"재생목록 ID: {playlist_id}\n"
            f"URL: {pl_url}\n"
            f"총 {_format_number(total)}개 동영상 중 {len(items)}개 표시\n"
        ]

        for i, item in enumerate(items, 1):
            snippet = item.get("snippet", {})
            content = item.get("contentDetails", {})
            title = snippet.get("title", "(제목 없음)")
            channel = snippet.get("videoOwnerChannelTitle", "?")
            video_id = content.get("videoId", "")
            published = _format_publish_date(snippet.get("publishedAt", ""))
            position = snippet.get("position", i - 1) + 1
            url = f"https://www.youtube.com/watch?v={video_id}"

            lines.append(
                f"{position}. {title}\n"
                f"   채널: {channel} | 추가일: {published}\n"
                f"   URL: {url} | ID: {video_id}"
            )

        return "\n\n".join(lines)
    except Exception as e:
        logger.error("youtube_playlist_items failed: %s", e, exc_info=True)
        return f"재생목록 조회 중 오류가 발생했습니다: {e}"


@tool
def youtube_channel_videos(
    channel_id: str,
    max_results: int = 10,
    order: str = "date",
) -> str:
    """특정 YouTube 채널의 최근 동영상 목록을 조회합니다.

    Args:
        channel_id: 채널 ID (UCxxxxxxxx 형식) 또는 채널 핸들(@username)
        max_results: 반환할 동영상 수 (1~50, 기본값: 10)
        order: 정렬 기준 - date(최신순, 기본), viewCount(조회수순), rating(평점순)
    """
    try:
        channel_id = channel_id.strip()

        # @핸들 → 채널 ID 변환
        if channel_id.startswith("@") or not channel_id.startswith("UC"):
            handle = channel_id.lstrip("@")
            search_params = {
                "part": "snippet",
                "q": handle,
                "type": "channel",
                "maxResults": 1,
            }
            search_data = _fetch_json(_build_url("search", search_params))
            search_items = search_data.get("items", [])
            if not search_items:
                return f"채널 '{channel_id}'을(를) 찾을 수 없습니다."
            channel_id = search_items[0]["snippet"]["channelId"]

        max_results = max(1, min(max_results, 50))
        params: dict = {
            "part": "snippet",
            "channelId": channel_id,
            "type": "video",
            "order": order,
            "maxResults": max_results,
        }

        data = _fetch_json(_build_url("search", params))
        items = data.get("items", [])

        if not items:
            return f"채널 ID '{channel_id}'의 동영상을 찾을 수 없습니다."

        channel_url = f"https://www.youtube.com/channel/{channel_id}"
        lines = [
            f"📺 채널 동영상 목록\n"
            f"채널 ID: {channel_id} | URL: {channel_url}\n"
            f"정렬: {'최신순' if order == 'date' else '조회수순' if order == 'viewCount' else order} | {len(items)}개 표시\n"
        ]

        for i, item in enumerate(items, 1):
            snippet = item.get("snippet", {})
            video_id = item.get("id", {}).get("videoId", "")
            title = snippet.get("title", "(제목 없음)")
            published = _format_publish_date(snippet.get("publishedAt", ""))
            description = snippet.get("description", "")[:100].replace("\n", " ")
            url = f"https://www.youtube.com/watch?v={video_id}"

            lines.append(
                f"{i}. {title}\n"
                f"   업로드: {published}\n"
                f"   설명: {description}{'...' if len(snippet.get('description','')) > 100 else ''}\n"
                f"   URL: {url} | ID: {video_id}"
            )

        return "\n\n".join(lines)
    except Exception as e:
        logger.error("youtube_channel_videos failed: %s", e, exc_info=True)
        return f"채널 동영상 조회 중 오류가 발생했습니다: {e}"


# ── 도구 등록 ──────────────────────────────────────────────────────────────────

def get_tools() -> list:
    """YouTube 스킬 도구 목록을 반환합니다."""
    return [
        youtube_search,
        youtube_video_info,
        youtube_channel_info,
        youtube_trending,
        youtube_comments,
        youtube_playlist_items,
        youtube_channel_videos,
    ]
