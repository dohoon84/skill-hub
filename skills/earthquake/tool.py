from __future__ import annotations

import json
import logging
import urllib.request
import urllib.parse
from datetime import datetime, timedelta, timezone

from langchain_core.tools import tool

logger = logging.getLogger(__name__)

_USGS_URL = "https://earthquake.usgs.gov/fdsnws/event/1/query"


def _fetch_json(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "OpenChiken/1.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())


def _magnitude_label(mag: float) -> str:
    if mag < 4.5:
        return "경미"
    elif mag < 6.0:
        return "중간"
    elif mag < 7.0:
        return "강함 ⚠️"
    elif mag < 8.0:
        return "대규모 🚨"
    else:
        return "초대형 🆘"


@tool
def get_earthquakes(min_magnitude: float = 4.5, hours: int = 24, limit: int = 10) -> str:
    """Get recent earthquake data from USGS.
    Uses the USGS Earthquake Hazards Program API (free, no API key required).
    Args:
        min_magnitude: Minimum magnitude to filter (default: 4.5, range: 2.5~9.0)
        hours: Time range in hours from now (default: 24)
        limit: Maximum number of results to return (default: 10, max: 50)
    """
    try:
        limit = max(1, min(limit, 50))
        hours = max(1, min(hours, 168))
        min_magnitude = max(2.0, min(min_magnitude, 9.0))

        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(hours=hours)

        params = urllib.parse.urlencode({
            "format": "geojson",
            "starttime": start_time.strftime("%Y-%m-%dT%H:%M:%S"),
            "endtime": end_time.strftime("%Y-%m-%dT%H:%M:%S"),
            "minmagnitude": min_magnitude,
            "orderby": "magnitude",
            "limit": limit,
        })

        data = _fetch_json(f"{_USGS_URL}?{params}")
        features = data.get("features", [])

        if not features:
            return f"최근 {hours}시간 이내 규모 {min_magnitude}+ 지진 없음"

        lines = [f"🌋 최근 {hours}H 지진 현황 (M{min_magnitude}+, {len(features)}건)"]

        for eq in features:
            props = eq.get("properties", {})
            coords = eq.get("geometry", {}).get("coordinates", [0, 0, 0])
            mag = props.get("mag", 0)
            place = props.get("place", "위치 불명")
            time_ms = props.get("time", 0)
            depth = coords[2] if len(coords) > 2 else 0
            tsunami = props.get("tsunami", 0)
            label = _magnitude_label(mag)

            eq_time = datetime.fromtimestamp(time_ms / 1000, tz=timezone.utc).strftime("%m/%d %H:%M UTC")
            tsunami_str = " 🌊쓰나미 가능" if tsunami else ""
            lines.append(f"  M{mag:.1f} [{label}] {place}")
            lines.append(f"       시간: {eq_time} | 깊이: {depth:.1f}km{tsunami_str}")

        return "\n".join(lines)
    except Exception as e:
        logger.error("get_earthquakes failed: %s", e, exc_info=True)
        return f"지진 데이터 조회 실패: {e}"


@tool
def get_earthquake_summary(hours: int = 24) -> str:
    """Get a summary of global earthquake activity for the past N hours.
    Args:
        hours: Time range in hours (default: 24)
    """
    try:
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(hours=hours)

        params = urllib.parse.urlencode({
            "format": "geojson",
            "starttime": start_time.strftime("%Y-%m-%dT%H:%M:%S"),
            "endtime": end_time.strftime("%Y-%m-%dT%H:%M:%S"),
            "minmagnitude": 2.5,
            "orderby": "time",
            "limit": 200,
        })

        data = _fetch_json(f"{_USGS_URL}?{params}")
        features = data.get("features", [])

        if not features:
            return f"최근 {hours}시간 이내 규모 2.5+ 지진 없음"

        buckets = {"2.5~3.9": 0, "4.0~4.9": 0, "5.0~5.9": 0, "6.0~6.9": 0, "7.0+": 0}
        max_mag = 0.0
        max_place = ""
        for eq in features:
            m = eq["properties"].get("mag", 0) or 0
            if m >= 7.0:
                buckets["7.0+"] += 1
            elif m >= 6.0:
                buckets["6.0~6.9"] += 1
            elif m >= 5.0:
                buckets["5.0~5.9"] += 1
            elif m >= 4.0:
                buckets["4.0~4.9"] += 1
            else:
                buckets["2.5~3.9"] += 1
            if m > max_mag:
                max_mag = m
                max_place = eq["properties"].get("place", "")

        lines = [
            f"🌍 지진 활동 요약 (최근 {hours}H, 총 {len(features)}건)",
            f"  최대 규모: M{max_mag:.1f} — {max_place}",
            "  규모별 분포:",
        ]
        for k, v in buckets.items():
            if v > 0:
                lines.append(f"    M{k}: {v}건")

        return "\n".join(lines)
    except Exception as e:
        logger.error("get_earthquake_summary failed: %s", e, exc_info=True)
        return f"지진 요약 조회 실패: {e}"


def get_tools() -> list:
    return [get_earthquakes, get_earthquake_summary]
