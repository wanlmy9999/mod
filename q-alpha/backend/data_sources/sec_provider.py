"""
SEC EDGAR Data Provider
Fetches insider trading, institutional holdings, risk factors from SEC.
No API key required for public EDGAR endpoints.
"""

import logging
import requests
from typing import Any, Optional
from data_sources.provider import BaseProvider

logger = logging.getLogger("q-alpha.sec")

SEC_BASE = "https://data.sec.gov"
HEADERS = {
    "User-Agent": "Q-Alpha admin@qalpha.io",
    "Accept-Encoding": "gzip, deflate",
}


class SECProvider(BaseProvider):
    name = "sec"

    def is_available(self) -> bool:
        return True  # Public SEC API, no key needed

    def fetch(self, endpoint: str, params: dict) -> Optional[Any]:
        ticker = params.get("ticker", "AAPL").upper()

        if endpoint == "insider":
            return self._get_insider_trades(ticker)
        elif endpoint == "sec":
            return self._get_sec_filings(ticker)
        elif endpoint == "institutional":
            return self._get_institutional(ticker)
        return None

    def _get_cik(self, ticker: str) -> Optional[str]:
        """Get CIK number for a ticker."""
        try:
            url = f"https://efts.sec.gov/LATEST/search-index?q=%22{ticker}%22&dateRange=custom&startdt=2020-01-01&forms=10-K"
            resp = requests.get(
                f"{SEC_BASE}/submissions/",
                headers=HEADERS,
                timeout=10,
            )
            # Try tickers.json
            tickers_url = "https://www.sec.gov/files/company_tickers.json"
            r = requests.get(tickers_url, headers=HEADERS, timeout=10)
            data = r.json()
            for item in data.values():
                if item.get("ticker", "").upper() == ticker.upper():
                    cik = str(item["cik_str"]).zfill(10)
                    return cik
        except Exception as e:
            logger.warning(f"CIK lookup failed for {ticker}: {e}")
        return None

    def _get_insider_trades(self, ticker: str) -> list:
        """Fetch Form 4 insider transactions from SEC EDGAR."""
        cik = self._get_cik(ticker)
        if not cik:
            return []

        try:
            url = f"{SEC_BASE}/submissions/CIK{cik}.json"
            r = requests.get(url, headers=HEADERS, timeout=10)
            data = r.json()

            filings = data.get("filings", {}).get("recent", {})
            forms = filings.get("form", [])
            dates = filings.get("filingDate", [])
            accessions = filings.get("accessionNumber", [])

            results = []
            for i, form in enumerate(forms):
                if form == "4" and len(results) < 20:
                    results.append({
                        "type": "Form 4",
                        "date": dates[i] if i < len(dates) else "",
                        "accession": accessions[i] if i < len(accessions) else "",
                        "ticker": ticker,
                    })
            return results
        except Exception as e:
            logger.warning(f"Insider data failed for {ticker}: {e}")
            return []

    def _get_sec_filings(self, ticker: str) -> list:
        """Get recent SEC filings (10-K, 10-Q, 8-K)."""
        cik = self._get_cik(ticker)
        if not cik:
            return []
        try:
            url = f"{SEC_BASE}/submissions/CIK{cik}.json"
            r = requests.get(url, headers=HEADERS, timeout=10)
            data = r.json()
            filings = data.get("filings", {}).get("recent", {})
            forms = filings.get("form", [])
            dates = filings.get("filingDate", [])
            descriptions = filings.get("primaryDocument", [])
            results = []
            for i, form in enumerate(forms):
                if form in ("10-K", "10-Q", "8-K") and len(results) < 15:
                    results.append({
                        "form": form,
                        "date": dates[i],
                        "document": descriptions[i] if i < len(descriptions) else "",
                        "url": f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/",
                    })
            return results
        except Exception as e:
            logger.warning(f"SEC filings failed for {ticker}: {e}")
            return []

    def _get_institutional(self, ticker: str) -> list:
        """Mock institutional holdings (13F parsing requires complex SEC logic)."""
        return []
