"""
轻量爬虫数据提供商（低频）
- Reddit: 通过公开搜索页抓取讨论
- CapitolTrades / QuiverQuant: 抓取公开页面标题与链接
- OpenSecrets: 抓取公开搜索结果摘要
"""

from __future__ import annotations

import logging
import time
from typing import Optional
from urllib.parse import quote_plus

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger("q-alpha.scraper")


class WebScraperProvider:
    name = "scraper"

    def __init__(self):
        self._session = requests.Session()
        self._session.headers.update(
            {
                "User-Agent": (
                    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
                )
            }
        )

    def is_available(self) -> bool:
        return True

    def _get(self, url: str, timeout: int = 12) -> Optional[str]:
        try:
            time.sleep(0.8)  # 降低抓取频率
            r = self._session.get(url, timeout=timeout)
            r.raise_for_status()
            return r.text
        except Exception as e:
            logger.warning(f"Scraper request failed: {url} -> {e}")
            return None

    def get_reddit_stock_mentions(self, keyword: str) -> Optional[list]:
        q = quote_plus(keyword)
        html = self._get(f"https://www.reddit.com/search/?q={q}&sort=new")
        if not html:
            return None
        soup = BeautifulSoup(html, "html.parser")
        items = []
        for a in soup.select("a[href*='/r/']")[:15]:
            title = (a.get_text() or "").strip()
            href = a.get("href", "")
            if not title:
                continue
            if href.startswith("/"):
                href = f"https://www.reddit.com{href}"
            items.append({"title": title, "url": href, "source": "reddit-scrape"})
        return items or None

    def get_capitol_trades(self, member_name: str = "") -> Optional[list]:
        html = self._get("https://www.capitoltrades.com/trades")
        if not html:
            return None
        soup = BeautifulSoup(html, "html.parser")
        links = []
        for a in soup.select("a[href]")[:200]:
            text = (a.get_text() or "").strip()
            href = a.get("href", "")
            if not text or "trade" not in text.lower():
                continue
            if member_name and member_name.lower() not in text.lower():
                continue
            if href.startswith("/"):
                href = f"https://www.capitoltrades.com{href}"
            links.append({"politician": text, "url": href, "source": "capitoltrades-scrape"})
            if len(links) >= 20:
                break
        return links or None

    def get_quiver_headlines(self, keyword: str = "") -> Optional[list]:
        html = self._get("https://www.quiverquant.com/home/")
        if not html:
            return None
        soup = BeautifulSoup(html, "html.parser")
        rows = []
        for a in soup.select("a[href]")[:200]:
            text = (a.get_text() or "").strip()
            href = a.get("href", "")
            if not text:
                continue
            if keyword and keyword.lower() not in text.lower():
                continue
            if href.startswith("/"):
                href = f"https://www.quiverquant.com{href}"
            rows.append({"title": text, "url": href, "source": "quiver-scrape"})
            if len(rows) >= 20:
                break
        return rows or None

    def get_opensecrets(self, company_name: str) -> Optional[list]:
        q = quote_plus(company_name)
        html = self._get(f"https://www.opensecrets.org/search?q={q}")
        if not html:
            return None
        soup = BeautifulSoup(html, "html.parser")
        rows = []
        for a in soup.select("a[href]")[:200]:
            text = (a.get_text() or "").strip()
            href = a.get("href", "")
            if not text:
                continue
            if company_name and company_name.lower() not in text.lower():
                continue
            if href.startswith("/"):
                href = f"https://www.opensecrets.org{href}"
            rows.append({"title": text, "url": href, "source": "opensecrets-scrape"})
            if len(rows) >= 20:
                break
        return rows or None

    def get_trends_proxy(self, keyword: str) -> Optional[dict]:
        # Google Trends API 不可用时，用 Reddit + Quiver 的公开热度代理
        reddit = self.get_reddit_stock_mentions(keyword) or []
        quiver = self.get_quiver_headlines(keyword) or []
        score = min(100, len(reddit) * 3 + len(quiver) * 2)
        return {
            "keyword": keyword,
            "proxy_interest": score,
            "reddit_count": len(reddit),
            "quiver_count": len(quiver),
            "source": "scraper-proxy",
            "samples": (reddit[:5] + quiver[:5]),
        }
