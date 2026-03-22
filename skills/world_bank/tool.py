from __future__ import annotations

import json
import logging
import urllib.request
import urllib.parse

from langchain_core.tools import tool

logger = logging.getLogger(__name__)

_BASE_URL = "https://api.worldbank.org/v2"

_INDICATORS = {
    "gdp_growth": ("NY.GDP.MKTP.KD.ZG", "GDP 성장률(%)"),
    "inflation": ("FP.CPI.TOTL.ZG", "소비자물가 상승률(%)"),
    "unemployment": ("SL.UEM.TOTL.ZS", "실업률(%)"),
    "gni_per_capita": ("NY.GNP.PCAP.CD", "1인당 GNI(USD)"),
    "exports": ("NE.EXP.GNFS.ZS", "수출(GDP 대비%)"),
    "govt_debt": ("GC.DOD.TOTL.GD.ZS", "정부부채(GDP 대비%)"),
}

_COUNTRY_NAMES = {
    "KR": "한국", "US": "미국", "CN": "중국", "JP": "일본",
    "DE": "독일", "GB": "영국", "FR": "프랑스", "IN": "인도",
    "SG": "싱가포르", "AU": "호주", "BR": "브라질",
}


def _fetch_json(url: str) -> list:
    req = urllib.request.Request(url, headers={"User-Agent": "OpenChiken/1.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())


def _get_indicator(country_code: str, indicator_code: str, years: int = 5) -> list[tuple[str, float]]:
    url = f"{_BASE_URL}/country/{country_code}/indicator/{indicator_code}?format=json&mrv={years}&per_page={years}"
    data = _fetch_json(url)
    if not data or len(data) < 2:
        return []
    entries = data[1] or []
    return [
        (e["date"], e["value"])
        for e in entries
        if e.get("value") is not None
    ]


@tool
def get_world_bank_data(country_code: str, indicators: str = "all") -> str:
    """Get macroeconomic indicators from the World Bank for a specific country.
    Uses the World Bank public API (free, no API key required).
    Args:
        country_code: ISO 3166-1 alpha-2 country code (e.g. KR, US, CN, JP, DE, GB)
        indicators: Comma-separated list of indicators or 'all' for main set.
                    Options: gdp_growth, inflation, unemployment, gni_per_capita, exports, govt_debt
    """
    try:
        country_code = country_code.upper()
        country_name = _COUNTRY_NAMES.get(country_code, country_code)

        if indicators.strip().lower() == "all":
            selected = list(_INDICATORS.keys())
        else:
            selected = [i.strip() for i in indicators.split(",") if i.strip() in _INDICATORS]
            if not selected:
                return f"유효한 지표를 입력하세요: {', '.join(_INDICATORS.keys())}"

        lines = [f"🌐 {country_name}({country_code}) 거시경제 지표 (World Bank)"]

        for key in selected:
            code, label = _INDICATORS[key]
            values = _get_indicator(country_code, code, years=3)
            if not values:
                lines.append(f"  {label}: 데이터 없음")
                continue
            latest_year, latest_val = values[0]
            val_str = f"{latest_val:.1f}" if key not in ("gni_per_capita",) else f"${latest_val:,.0f}"
            trend = ""
            if len(values) >= 2:
                prev_val = values[1][1]
                diff = latest_val - prev_val
                trend = f" ({'▲' if diff > 0 else '▼'}{abs(diff):.1f})"
            lines.append(f"  {label}: {val_str} ({latest_year}){trend}")

        return "\n".join(lines)
    except Exception as e:
        logger.error("get_world_bank_data failed: %s", e, exc_info=True)
        return f"World Bank 데이터 조회 실패: {e}"


@tool
def compare_countries(country_codes: str, indicator: str = "gdp_growth") -> str:
    """Compare a specific economic indicator across multiple countries.
    Args:
        country_codes: Comma-separated country codes (e.g. 'KR,US,CN,JP')
        indicator: Indicator to compare (gdp_growth, inflation, unemployment, gni_per_capita, exports, govt_debt)
    """
    try:
        codes = [c.strip().upper() for c in country_codes.split(",") if c.strip()][:6]
        if not codes:
            return "국가 코드를 쉼표로 구분하여 입력하세요. 예: KR,US,CN,JP"

        if indicator not in _INDICATORS:
            return f"유효한 지표: {', '.join(_INDICATORS.keys())}"

        ind_code, label = _INDICATORS[indicator]
        lines = [f"📊 국가별 {label} 비교"]

        results = []
        for code in codes:
            name = _COUNTRY_NAMES.get(code, code)
            values = _get_indicator(code, ind_code, years=1)
            if values:
                year, val = values[0]
                results.append((name, code, year, val))
            else:
                lines.append(f"  {name}: 데이터 없음")

        results.sort(key=lambda x: x[3], reverse=True)
        for i, (name, code, year, val) in enumerate(results, 1):
            val_str = f"{val:.1f}" if indicator != "gni_per_capita" else f"${val:,.0f}"
            lines.append(f"  {i}. {name}({code}): {val_str} ({year})")

        return "\n".join(lines)
    except Exception as e:
        logger.error("compare_countries failed: %s", e, exc_info=True)
        return f"국가 비교 조회 실패: {e}"


def get_tools() -> list:
    return [get_world_bank_data, compare_countries]
