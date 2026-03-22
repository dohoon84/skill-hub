from __future__ import annotations

import json
import logging
import urllib.request

from langchain_core.tools import tool

logger = logging.getLogger(__name__)

_EDGAR_BASE = "https://data.sec.gov"
_COMPANY_SEARCH = "https://efts.sec.gov/LATEST/search-index?q=%22{ticker}%22&dateRange=custom&startdt=2020-01-01&forms=10-K"


def _fetch_json(url: str) -> dict:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "OpenChiken research@openchiken.dev", "Accept": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())


def _get_cik(ticker: str) -> str | None:
    try:
        data = _fetch_json(f"{_EDGAR_BASE}/submissions/CIK{ticker.upper().zfill(10)}.json")
        return data.get("cik")
    except Exception:
        pass
    try:
        tickers_data = _fetch_json("https://www.sec.gov/files/company_tickers.json")
        for item in tickers_data.values():
            if item.get("ticker", "").upper() == ticker.upper():
                return str(item["cik_str"]).zfill(10)
    except Exception:
        pass
    return None


def _format_number(n: float | None) -> str:
    if n is None:
        return "N/A"
    if abs(n) >= 1_000_000_000:
        return f"${n / 1_000_000_000:.2f}B"
    elif abs(n) >= 1_000_000:
        return f"${n / 1_000_000:.1f}M"
    else:
        return f"${n:,.0f}"


@tool
def get_sec_filings(ticker: str, form_type: str = "10-K") -> str:
    """Get SEC filing data for a US publicly traded company.
    Uses the SEC EDGAR public API (free, no API key required).
    Args:
        ticker: Stock ticker symbol (e.g. AAPL, TSLA, NVDA, MSFT, AMZN)
        form_type: Filing type - '10-K' (annual), '10-Q' (quarterly), '8-K' (current report)
    """
    try:
        ticker = ticker.upper()
        cik = _get_cik(ticker)
        if not cik:
            return f"'{ticker}' 티커에 해당하는 기업을 SEC EDGAR에서 찾을 수 없습니다."

        cik_padded = cik.zfill(10)
        submissions = _fetch_json(f"{_EDGAR_BASE}/submissions/CIK{cik_padded}.json")
        company_name = submissions.get("name", ticker)

        filings = submissions.get("filings", {}).get("recent", {})
        forms = filings.get("form", [])
        dates = filings.get("filingDate", [])
        accnums = filings.get("accessionNumber", [])

        matching = [(dates[i], accnums[i]) for i, f in enumerate(forms) if f == form_type]
        if not matching:
            return f"{ticker} ({company_name})의 {form_type} 보고서를 찾을 수 없습니다."

        latest_date, latest_accn = matching[0]
        accn_clean = latest_accn.replace("-", "")
        filing_url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accn_clean}/"
        edgar_url = f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={cik_padded}&type={form_type}&dateb=&owner=include&count=5"

        facts_data = _fetch_json(f"{_EDGAR_BASE}/api/xbrl/companyfacts/CIK{cik_padded}.json")
        us_gaap = facts_data.get("facts", {}).get("us-gaap", {})

        def latest_value(concept: str) -> float | None:
            c = us_gaap.get(concept, {})
            units = c.get("units", {})
            for unit_key in ["USD", "shares"]:
                entries = units.get(unit_key, [])
                annual = [e for e in entries if e.get("form") == "10-K" and e.get("fp") == "FY"]
                if annual:
                    annual.sort(key=lambda x: x.get("end", ""), reverse=True)
                    return annual[0].get("val")
            return None

        revenue = latest_value("Revenues") or latest_value("RevenueFromContractWithCustomerExcludingAssessedTax")
        net_income = latest_value("NetIncomeLoss")
        operating_income = latest_value("OperatingIncomeLoss")
        total_assets = latest_value("Assets")
        total_liabilities = latest_value("Liabilities")
        eps = latest_value("EarningsPerShareBasic")

        lines = [
            f"📋 {company_name} ({ticker}) — {form_type} ({latest_date})",
            f"🔗 SEC EDGAR: {edgar_url}",
            "",
            "💰 재무 현황 (연간)",
        ]

        if revenue:
            lines.append(f"  매출액:      {_format_number(revenue)}")
        if net_income:
            margin = (net_income / revenue * 100) if revenue else None
            margin_str = f"  (순이익률 {margin:.1f}%)" if margin else ""
            lines.append(f"  순이익:      {_format_number(net_income)}{margin_str}")
        if operating_income:
            op_margin = (operating_income / revenue * 100) if revenue else None
            op_str = f"  (영업이익률 {op_margin:.1f}%)" if op_margin else ""
            lines.append(f"  영업이익:    {_format_number(operating_income)}{op_str}")
        if total_assets:
            lines.append(f"  총자산:      {_format_number(total_assets)}")
        if total_liabilities and total_assets:
            debt_ratio = total_liabilities / total_assets * 100
            lines.append(f"  총부채:      {_format_number(total_liabilities)}  (부채비율 {debt_ratio:.1f}%)")
        if eps:
            lines.append(f"  EPS(기본):   ${eps:.2f}")

        if not any([revenue, net_income, operating_income]):
            lines.append("  재무 상세 데이터 조회 불가 — SEC 직접 확인 권장")
            lines.append(f"  최신 보고서: {filing_url}")

        return "\n".join(lines)
    except Exception as e:
        logger.error("get_sec_filings failed: %s", e, exc_info=True)
        return f"SEC EDGAR 조회 실패: {e}"


def get_tools() -> list:
    return [get_sec_filings]
