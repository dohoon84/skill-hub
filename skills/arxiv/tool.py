from __future__ import annotations

import logging
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime

from langchain_core.tools import tool

logger = logging.getLogger(__name__)

_BASE_URL = "http://export.arxiv.org/api/query"
_NS = {"atom": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}


def _fetch_xml(url: str) -> ET.Element:
    req = urllib.request.Request(url, headers={"User-Agent": "OpenChiken/1.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return ET.fromstring(resp.read())


@tool
def search_arxiv(query: str, max_results: int = 5, category: str = "") -> str:
    """Search academic papers on arXiv.
    Uses the arXiv public API (free, no API key required).
    Args:
        query: Search keywords (e.g. 'large language model', 'diffusion model', 'transformer')
        max_results: Number of papers to return (default: 5, max: 20)
        category: arXiv category filter (optional, e.g. cs.AI, cs.LG, cs.CL, quant-ph)
    """
    try:
        max_results = max(1, min(max_results, 20))
        search_query = urllib.parse.quote(query)
        if category:
            search_query = f"cat:{category}+AND+{search_query}"

        params = urllib.parse.urlencode({
            "search_query": f"all:{urllib.parse.unquote(search_query)}" if not category else f"cat:{category} AND all:{query}",
            "start": 0,
            "max_results": max_results,
            "sortBy": "submittedDate",
            "sortOrder": "descending",
        })

        root = _fetch_xml(f"{_BASE_URL}?{params}")
        entries = root.findall("atom:entry", _NS)

        if not entries:
            return f"'{query}' 관련 논문을 찾을 수 없습니다."

        lines = [f"🔬 arXiv 논문 검색: '{query}' ({len(entries)}건)"]
        for i, entry in enumerate(entries, 1):
            title = (entry.findtext("atom:title", "", _NS) or "").replace("\n", " ").strip()
            abstract = (entry.findtext("atom:summary", "", _NS) or "").replace("\n", " ").strip()
            authors = [a.findtext("atom:name", "", _NS) for a in entry.findall("atom:author", _NS)]
            published = entry.findtext("atom:published", "", _NS)[:10]
            link = entry.findtext("atom:id", "", _NS)
            cats = [c.get("term", "") for c in entry.findall("atom:category", _NS)]

            abstract_short = abstract[:200] + "..." if len(abstract) > 200 else abstract
            author_str = ", ".join(authors[:3]) + (" 외" if len(authors) > 3 else "")
            cat_str = ", ".join(cats[:3])

            lines.append(f"\n{i}. [{published}] {title}")
            lines.append(f"   저자: {author_str}")
            lines.append(f"   카테고리: {cat_str}")
            lines.append(f"   요약: {abstract_short}")
            lines.append(f"   링크: {link}")

        return "\n".join(lines)
    except Exception as e:
        logger.error("search_arxiv failed: %s", e, exc_info=True)
        return f"arXiv 검색 실패: {e}"


@tool
def get_arxiv_paper(arxiv_id: str) -> str:
    """Get details of a specific arXiv paper by its ID.
    Args:
        arxiv_id: arXiv paper ID (e.g. '2303.08774' or 'https://arxiv.org/abs/2303.08774')
    """
    try:
        paper_id = arxiv_id.strip().replace("https://arxiv.org/abs/", "").replace("http://arxiv.org/abs/", "")
        params = urllib.parse.urlencode({"id_list": paper_id})
        root = _fetch_xml(f"{_BASE_URL}?{params}")

        entries = root.findall("atom:entry", _NS)
        if not entries:
            return f"arXiv ID '{paper_id}'를 찾을 수 없습니다."

        entry = entries[0]
        title = (entry.findtext("atom:title", "", _NS) or "").replace("\n", " ").strip()
        abstract = (entry.findtext("atom:summary", "", _NS) or "").replace("\n", " ").strip()
        authors = [a.findtext("atom:name", "", _NS) for a in entry.findall("atom:author", _NS)]
        published = entry.findtext("atom:published", "", _NS)[:10]
        updated = entry.findtext("atom:updated", "", _NS)[:10]
        link = entry.findtext("atom:id", "", _NS)
        cats = [c.get("term", "") for c in entry.findall("atom:category", _NS)]

        author_str = ", ".join(authors[:5]) + (" 외" if len(authors) > 5 else "")

        return (
            f"📄 {title}\n"
            f"저자: {author_str}\n"
            f"발표: {published} (최종수정: {updated})\n"
            f"카테고리: {', '.join(cats)}\n"
            f"링크: {link}\n\n"
            f"초록:\n{abstract}"
        )
    except Exception as e:
        logger.error("get_arxiv_paper failed: %s", e, exc_info=True)
        return f"arXiv 논문 조회 실패: {e}"


def get_tools() -> list:
    return [search_arxiv, get_arxiv_paper]
