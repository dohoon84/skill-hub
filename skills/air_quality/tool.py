from __future__ import annotations

import json
import logging
import urllib.request
import urllib.parse

from langchain_core.tools import tool

logger = logging.getLogger(__name__)

_BASE_URL = "https://api.openaq.org/v3"


def _fetch_json(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "OpenChiken/1.0", "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())


def _aqi_level(aqi: float) -> str:
    if aqi <= 50:
        return "좋음 🟢"
    elif aqi <= 100:
        return "보통 🟡"
    elif aqi <= 150:
        return "민감군 주의 🟠"
    elif aqi <= 200:
        return "나쁨 🔴"
    elif aqi <= 300:
        return "매우 나쁨 🟣"
    else:
        return "위험 ⛔"


@tool
def get_air_quality(city: str) -> str:
    """Get current air quality data for a specific city.
    Uses the OpenAQ public API (free, no API key required).
    Returns PM2.5, PM10, AQI and other pollutant levels.
    Args:
        city: City name in English (e.g. Seoul, Beijing, Delhi, Tokyo, London)
    """
    try:
        encoded_city = urllib.parse.quote(city)
        data = _fetch_json(f"{_BASE_URL}/locations?city={encoded_city}&limit=5&order_by=lastUpdated&sort=desc")

        results = data.get("results", [])
        if not results:
            return f"'{city}'의 대기질 데이터를 찾을 수 없습니다. 도시명을 영문으로 입력하세요."

        location = results[0]
        loc_name = location.get("name", city)
        country = location.get("country", {}).get("name", "")
        last_updated = location.get("datetimeLast", {}).get("local", "")[:16] if location.get("datetimeLast") else "N/A"

        sensors = location.get("sensors", [])
        params: dict[str, float] = {}
        for sensor in sensors:
            param = sensor.get("parameter", {})
            param_name = param.get("name", "").lower()
            latest = sensor.get("latest", {})
            value = latest.get("value")
            if value is not None:
                params[param_name] = round(float(value), 2)

        lines = [f"🌫️ {city} ({country}) 대기질 현황", f"📍 측정소: {loc_name} | 업데이트: {last_updated}"]

        pm25 = params.get("pm25") or params.get("pm2.5")
        pm10 = params.get("pm10")
        no2 = params.get("no2")
        o3 = params.get("o3")
        co = params.get("co")

        if pm25 is not None:
            aqi_approx = pm25 * 4 if pm25 <= 12 else pm25 * 3
            level = _aqi_level(aqi_approx)
            lines.append(f"  PM2.5: {pm25} μg/m³  |  AQI(추정): {int(aqi_approx)} — {level}")
        if pm10 is not None:
            lines.append(f"  PM10: {pm10} μg/m³")
        if no2 is not None:
            lines.append(f"  NO₂: {no2} μg/m³")
        if o3 is not None:
            lines.append(f"  O₃: {o3} μg/m³")
        if co is not None:
            lines.append(f"  CO: {co} μg/m³")

        if not params:
            lines.append("  현재 측정 데이터 없음")

        return "\n".join(lines)
    except Exception as e:
        logger.error("get_air_quality failed: %s", e, exc_info=True)
        return f"대기질 조회 실패: {e}"


@tool
def compare_air_quality(cities: str) -> str:
    """Compare air quality across multiple cities.
    Args:
        cities: Comma-separated list of city names in English (e.g. "Seoul,Tokyo,Beijing")
    """
    city_list = [c.strip() for c in cities.split(",") if c.strip()]
    if not city_list:
        return "도시 목록을 쉼표로 구분하여 입력하세요. 예: Seoul,Tokyo,Beijing"

    results = []
    for city in city_list[:5]:
        result = get_air_quality.invoke({"city": city})
        results.append(result)

    return "\n\n".join(results)


def get_tools() -> list:
    return [get_air_quality, compare_air_quality]
