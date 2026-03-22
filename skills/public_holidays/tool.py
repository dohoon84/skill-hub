from __future__ import annotations

import json
import logging
import urllib.request
from datetime import datetime

from langchain_core.tools import tool

logger = logging.getLogger(__name__)

_BASE_URL = "https://date.nager.at/api/v3"


def _fetch_json(url: str) -> list | dict:
    req = urllib.request.Request(url, headers={"User-Agent": "OpenChiken/1.0", "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read())


@tool
def get_public_holidays(country_code: str, year: int = 0) -> str:
    """Get public holidays for a specific country and year.
    Uses the Nager.Date API (free, no API key required). Supports 90+ countries.
    Args:
        country_code: ISO 3166-1 alpha-2 country code (e.g. KR, US, JP, DE, GB, SG)
        year: Year to query (default: current year)
    """
    try:
        if year == 0:
            year = datetime.now().year
        country_code = country_code.upper()

        data = _fetch_json(f"{_BASE_URL}/PublicHolidays/{year}/{country_code}")

        if not data:
            return f"{country_code}의 {year}년 공휴일 정보를 찾을 수 없습니다."

        lines = [f"📅 {country_code} {year}년 공휴일 ({len(data)}건)"]
        for h in data:
            date_str = h.get("date", "")
            name = h.get("localName") or h.get("name", "")
            global_name = h.get("name", "")
            fixed = "🔒" if h.get("fixed") else "📆"
            national = " (국경일)" if h.get("national") else ""
            line = f"{fixed} {date_str}  {name}"
            if global_name != name:
                line += f" ({global_name})"
            line += national
            lines.append(line)

        return "\n".join(lines)
    except Exception as e:
        logger.error("get_public_holidays failed: %s", e, exc_info=True)
        return f"공휴일 조회 실패: {e}"


@tool
def check_holiday(country_code: str, date: str) -> str:
    """Check if a specific date is a public holiday in a given country.
    Args:
        country_code: ISO 3166-1 alpha-2 country code (e.g. KR, US, JP)
        date: Date string in YYYY-MM-DD format
    """
    try:
        country_code = country_code.upper()
        year = int(date[:4])
        data = _fetch_json(f"{_BASE_URL}/PublicHolidays/{year}/{country_code}")

        for h in data:
            if h.get("date") == date:
                name = h.get("localName") or h.get("name", "")
                return f"✅ {date}은(는) {country_code}의 공휴일입니다: {name}"

        return f"ℹ️ {date}은(는) {country_code}의 공휴일이 아닙니다."
    except Exception as e:
        logger.error("check_holiday failed: %s", e, exc_info=True)
        return f"공휴일 확인 실패: {e}"


def get_tools() -> list:
    return [get_public_holidays, check_holiday]
