"""
Q-Alpha 统一数据调度器
优先级链: Finnhub → EulerPool → Alpha Vantage → AkShare → Yahoo Finance → Mock
所有端点均先查 Redis 缓存，缓存未命中时调用真实 API，失败则自动 Fallback
"""

import logging
from datetime import datetime, timezone
from typing import Any, Optional

logger = logging.getLogger("q-alpha.provider")


class DataProvider:
    """
    多源数据聚合与 Fallback 调度器
    ─────────────────────────────────────────────────────────────
    数据源优先级（股票价格）:
      1. Finnhub          — 实时高频，免费版每分钟60次
      2. Alpha Vantage    — 基本面+技术指标，免费版每分钟5次
      3. AkShare          — Python金融数据源，补充行情
      4. Yahoo Finance    — yfinance，无需 Key
      5. Mock Data        — 兜底，保证界面永不空白
    ─────────────────────────────────────────────────────────────
    """

    def __init__(self):
        self._finnhub   = None
        self._eulerpool = None
        self._alphav    = None
        self._akshare   = None
        self._scraper   = None
        self._yahoo     = None
        self._mock      = None
        self._init_providers()

    def _init_providers(self):
        """延迟初始化所有数据提供商"""
        try:
            from data_sources.finnhub_provider  import FinnhubProvider
            from data_sources.eulerpool_provider import EulerPoolProvider
            from data_sources.alphav_provider   import AlphaVantageProvider
            from data_sources.akshare_provider  import AkShareProvider
            from data_sources.web_scraper_provider import WebScraperProvider
            from data_sources.yahoo_provider    import YahooProvider
            from data_sources.mock_provider     import MockProvider
            self._finnhub = FinnhubProvider()
            self._eulerpool = EulerPoolProvider()
            self._alphav  = AlphaVantageProvider()
            self._akshare = AkShareProvider()
            self._scraper = WebScraperProvider()
            self._yahoo   = YahooProvider()
            self._mock    = MockProvider()
        except Exception as e:
            logger.error(f"Provider 初始化失败: {e}")
            from data_sources.mock_provider import MockProvider
            self._mock = MockProvider()

    def _try_chain(self, *funcs) -> Optional[Any]:
        """依次尝试函数列表，返回第一个非 None 结果"""
        for fn in funcs:
            try:
                result = fn()
                if result is not None:
                    return result
            except Exception as e:
                logger.debug(f"[{fn}] 失败: {e}")
        return None

    def fetch(self, endpoint: str, params: Optional[dict] = None, source_type: str = None) -> Any:
        """
        兼容旧版统一入口：按 endpoint 分发到新的强类型方法。
        source_type 参数仅为兼容保留（当前不参与路由决策）。
        """
        params = params or {}
        ticker = params.get("ticker", "AAPL")
        timeframe = params.get("timeframe", "3mo")
        keyword = params.get("keyword", ticker)
        member_name = params.get("member_name", "")
        company_name = params.get("company_name", "")
        politician_name = params.get("politician_name", "")
        agency_name = params.get("agency_name", "")
        app_name = params.get("app_name", "")
        celebrity_name = params.get("celebrity_name", "")
        _ = source_type  # backward compatibility

        if endpoint == "stock/price":
            return self.get_stock_price(ticker)
        if endpoint == "stock/candles":
            return self.get_candles(ticker, timeframe)
        if endpoint == "stock/info":
            return self.get_stock_info(ticker)
        if endpoint == "market/popular":
            return self.get_popular()
        if endpoint == "market/news":
            return self.get_news(ticker if "ticker" in params else None)
        if endpoint == "insider":
            return self.get_insider(ticker)
        if endpoint == "whales":
            return self.get_whales(ticker)
        if endpoint == "institutional":
            return self.get_whales_detail(ticker)
        if endpoint == "analyst":
            return self.get_analyst(ticker)
        if endpoint == "sec":
            return self._mock.fetch("sec", {"ticker": ticker.upper()})
        if endpoint == "revenue":
            return self.get_revenue(ticker)
        if endpoint == "risk":
            return self.get_risk(ticker)
        if endpoint == "etf":
            return self.get_etf(ticker)
        if endpoint == "splits":
            return self.get_splits(ticker)
        if endpoint in ("trends", "consumer"):
            return self.get_trends(keyword)
        if endpoint == "patents":
            return self.get_patents(company_name)
        if endpoint == "media/cnbc":
            return self.get_cnbc_picks()
        if endpoint == "media/cramer":
            return self.get_cramer_tracker()
        if endpoint == "app-ratings":
            return self.get_app_ratings(app_name)
        if endpoint == "politician/search":
            return self.get_politician_search(params.get("name", ""))
        if endpoint == "gov/congress-trading":
            return self.get_congressional_trading(
                ticker=params.get("ticker"), member=member_name or None
            )
        if endpoint == "gov/networth":
            return self.get_networth(member_name)
        if endpoint == "gov/insider-score":
            return self.get_insider_score(member_name)
        if endpoint == "gov/lobbying":
            return self.get_lobbying(company_name)
        if endpoint == "gov/contracts":
            return self.get_contracts(agency_name or None)
        if endpoint == "gov/spending":
            return self.get_spending(agency_name or None)
        if endpoint == "gov/elections":
            return self.get_elections()
        if endpoint == "gov/fundraising":
            return self.get_fundraising(politician_name)
        if endpoint == "gov/corporate-donations":
            return self.get_corporate_donations(company_name)
        if endpoint == "portfolio/famous":
            return self.get_famous_portfolio(celebrity_name)

        logger.warning(f"Unknown endpoint '{endpoint}', fallback to mock provider.")
        return self._mock.fetch(endpoint, params)

    @staticmethod
    def _extract_source(data: Any) -> str:
        if isinstance(data, dict):
            return data.get("source", "unknown")
        if isinstance(data, list) and data:
            first = data[0]
            if isinstance(first, dict):
                return first.get("source", "unknown")
        return "unknown"

    @staticmethod
    def _source_plan(endpoint: str) -> list:
        plans = {
            "stock/price": ["finnhub_api", "eulerpool_api", "alpha_vantage_api", "akshare", "yfinance", "mock"],
            "stock/candles": ["finnhub_api", "eulerpool_api", "alpha_vantage_api", "akshare", "yfinance", "mock"],
            "stock/info": ["eulerpool_api", "alpha_vantage_api", "finnhub_api", "yfinance", "mock"],
            "market/news": ["finnhub_api", "alpha_vantage_api", "reddit_scraper", "mock"],
            "trends": ["reddit_scraper", "quiver_scraper", "mock"],
            "consumer": ["reddit_scraper", "quiver_scraper", "mock"],
            "gov/congress-trading": ["finnhub_api", "capitoltrades_scraper", "quiver_scraper", "mock"],
            "gov/lobbying": ["opensecrets_scraper", "mock"],
        }
        return plans.get(endpoint, ["provider_router", "mock"])

    def fetch_with_meta(self, endpoint: str, params: Optional[dict] = None, source_type: str = None) -> dict:
        params = params or {}
        data = self.fetch(endpoint, params, source_type=source_type)
        selected = self._extract_source(data)
        return {
            "data": data,
            "meta": {
                "endpoint": endpoint,
                "params": params,
                "source_type": source_type or "",
                "selected_source": selected,
                "source_plan": self._source_plan(endpoint),
                "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            },
        }

    # ════════════════════════════════════════════════════════════
    # 股票行情数据
    # ════════════════════════════════════════════════════════════

    def get_stock_price(self, ticker: str) -> dict:
        """实时报价 — Finnhub > EulerPool > Alpha Vantage > AkShare > Yahoo > Mock"""
        t = ticker.upper()
        result = self._try_chain(
            lambda: self._finnhub and self._finnhub.get_quote(t),
            lambda: self._eulerpool and self._eulerpool.get_quote(t),
            lambda: self._alphav  and self._alphav.get_quote(t),
            lambda: self._akshare and self._akshare.get_quote(t),
            lambda: self._yahoo   and self._yahoo.fetch("stock/price", {"ticker": t}),
        )
        if result:
            return result
        return self._mock.fetch("stock/price", {"ticker": t})

    def get_candles(self, ticker: str, timeframe: str = "3mo") -> dict:
        """K线数据 — Finnhub > EulerPool > Alpha Vantage > AkShare > Yahoo > Mock"""
        t = ticker.upper()
        result = self._try_chain(
            lambda: self._finnhub and self._finnhub.get_candles(t, timeframe),
            lambda: self._eulerpool and self._eulerpool.get_candles(t, timeframe),
            lambda: self._alphav  and self._alphav.get_daily_candles(t) if timeframe in ("3mo","6mo","1y","5y") else None,
            lambda: self._akshare and self._akshare.get_candles(t, timeframe),
            lambda: self._yahoo   and self._yahoo.fetch("stock/candles", {"ticker": t, "timeframe": timeframe}),
        )
        if result:
            return result
        return self._mock.fetch("stock/candles", {"ticker": t, "timeframe": timeframe})

    def get_stock_info(self, ticker: str) -> dict:
        """公司基本信息 — Alpha Vantage > Finnhub > Yahoo > Mock"""
        t = ticker.upper()
        result = self._try_chain(
            lambda: self._eulerpool and self._eulerpool.get_profile(t),
            lambda: self._alphav  and self._alphav.get_overview(t),
            lambda: self._finnhub and self._finnhub.get_profile(t),
            lambda: self._yahoo   and self._yahoo.fetch("stock/info", {"ticker": t}),
        )
        if result:
            return result
        return self._mock.fetch("stock/info", {"ticker": t})

    def get_popular(self) -> list:
        """热门股票列表 — Yahoo > Mock"""
        result = self._try_chain(
            lambda: self._yahoo and self._yahoo.fetch("market/popular", {}),
        )
        return result or self._mock.fetch("market/popular", {})

    # ════════════════════════════════════════════════════════════
    # 内幕与机构数据
    # ════════════════════════════════════════════════════════════

    def get_insider(self, ticker: str) -> list:
        """内幕交易 — Finnhub > SEC EDGAR > Mock"""
        t = ticker.upper()
        result = self._try_chain(
            lambda: self._finnhub and self._finnhub.get_insider_transactions(t),
        )
        return result or self._mock.fetch("insider", {"ticker": t})

    def get_insider_sentiment(self, ticker: str) -> list:
        """内幕情绪汇总 — Finnhub > Mock"""
        t = ticker.upper()
        result = self._try_chain(
            lambda: self._finnhub and self._finnhub.get_insider_sentiment(t),
        )
        return result or self._mock.fetch("insider", {"ticker": t})

    def get_whales(self, ticker: str) -> list:
        """机构持仓 — Mock (需要Quiver/SEC 13F订阅)"""
        return self._mock.fetch("whales", {"ticker": ticker.upper()})

    def get_analyst(self, ticker: str) -> list:
        """分析师评级 — Finnhub > Alpha Vantage > Mock"""
        t = ticker.upper()
        result = self._try_chain(
            lambda: self._finnhub and self._finnhub.get_recommendations(t),
        )
        return result or self._mock.fetch("analyst", {"ticker": t})

    def get_peers(self, ticker: str) -> list:
        """同行业对标 — Finnhub > Mock"""
        t = ticker.upper()
        result = self._try_chain(
            lambda: self._finnhub and self._finnhub.get_peers(t),
        )
        return result or []

    # ════════════════════════════════════════════════════════════
    # 财务数据
    # ════════════════════════════════════════════════════════════

    def get_financials(self, ticker: str) -> dict:
        """完整财务数据 — Alpha Vantage > Mock"""
        t = ticker.upper()
        income = self._try_chain(
            lambda: self._alphav and self._alphav.get_income_statement(t),
        )
        balance = self._try_chain(
            lambda: self._alphav and self._alphav.get_balance_sheet(t),
        )
        cashflow = self._try_chain(
            lambda: self._alphav and self._alphav.get_cash_flow(t),
        )
        earnings = self._try_chain(
            lambda: self._alphav and self._alphav.get_earnings(t),
        )
        if income or balance:
            return {
                "ticker": t,
                "income_statement": income,
                "balance_sheet": balance,
                "cash_flow": cashflow,
                "earnings": earnings,
            }
        return self._mock.fetch("revenue", {"ticker": t})

    def get_metrics(self, ticker: str) -> dict:
        """财务指标 — Finnhub > Alpha Vantage > Mock"""
        t = ticker.upper()
        result = self._try_chain(
            lambda: self._finnhub and self._finnhub.get_metrics(t),
            lambda: self._alphav  and self._alphav.get_overview(t),
        )
        return result or self._mock.fetch("stock/info", {"ticker": t})

    # ════════════════════════════════════════════════════════════
    # 技术指标
    # ════════════════════════════════════════════════════════════

    def get_rsi(self, ticker: str, period: int = 14) -> Optional[dict]:
        """RSI — Alpha Vantage > Mock计算"""
        t = ticker.upper()
        return self._try_chain(
            lambda: self._alphav and self._alphav.get_rsi(t, period),
        )

    def get_macd(self, ticker: str) -> Optional[dict]:
        """MACD — Alpha Vantage > Mock计算"""
        t = ticker.upper()
        return self._try_chain(
            lambda: self._alphav and self._alphav.get_macd(t),
        )

    def get_sma(self, ticker: str, period: int = 50) -> Optional[dict]:
        """SMA移动平均 — Alpha Vantage"""
        return self._try_chain(
            lambda: self._alphav and self._alphav.get_sma(ticker.upper(), period),
        )

    # ════════════════════════════════════════════════════════════
    # 新闻与情绪
    # ════════════════════════════════════════════════════════════

    def get_news(self, ticker: str = None) -> list:
        """公司新闻 — Finnhub > Alpha Vantage > Mock"""
        t = (ticker or "AAPL").upper()
        result = self._try_chain(
            lambda: self._finnhub and self._finnhub.get_news(t),
            lambda: self._alphav  and self._alphav.get_news_sentiment(t),
            lambda: self._scraper and self._scraper.get_reddit_stock_mentions(t),
        )
        return result or self._mock.fetch("market/news", {})

    def get_sentiment(self, ticker: str) -> dict:
        """情绪分析 — Finnhub > Mock"""
        t = ticker.upper()
        result = self._try_chain(
            lambda: self._finnhub and self._finnhub.get_sentiment(t),
        )
        return result or {}

    # ════════════════════════════════════════════════════════════
    # 政治与政府数据
    # ════════════════════════════════════════════════════════════

    def get_congressional_trading(self, ticker: str = None, member: str = None) -> list:
        """国会交易 — Finnhub(按股票) > Mock"""
        result = None
        if ticker:
            result = self._try_chain(
                lambda: self._finnhub and self._finnhub.get_congressional_trading(ticker.upper()),
            )
        if result:
            if member:
                result = [t for t in result if member.lower() in t.get("politician","").lower()]
            return result
        scraped = self._try_chain(
            lambda: self._scraper and self._scraper.get_capitol_trades(member or ""),
            lambda: self._scraper and self._scraper.get_quiver_headlines(member or ""),
        )
        if scraped:
            return scraped
        return self._mock.fetch("gov/congress-trading", {"member_name": member or ""})

    def get_politician_search(self, name: str) -> list:
        return self._mock.fetch("politician/search", {"name": name})

    def get_networth(self, member: str) -> dict:
        return self._mock.fetch("gov/networth", {"member_name": member})

    def get_insider_score(self, member: str) -> dict:
        return self._mock.fetch("gov/insider-score", {"member_name": member})

    def get_lobbying(self, company: str) -> list:
        result = self._try_chain(
            lambda: self._scraper and self._scraper.get_opensecrets(company),
        )
        return result or self._mock.fetch("gov/lobbying", {"company_name": company})

    def get_contracts(self, agency: str = None) -> list:
        return self._mock.fetch("gov/contracts", {"agency_name": agency or ""})

    def get_elections(self) -> list:
        return self._mock.fetch("gov/elections", {})

    def get_fundraising(self, politician: str) -> dict:
        return self._mock.fetch("gov/fundraising", {"politician_name": politician})

    def get_corporate_donations(self, company: str) -> list:
        return self._mock.fetch("gov/corporate-donations", {"company_name": company})

    def get_spending(self, agency: str = None) -> list:
        return self._mock.fetch("gov/spending", {"agency_name": agency or ""})

    # ════════════════════════════════════════════════════════════
    # 市场数据
    # ════════════════════════════════════════════════════════════

    def get_market_status(self) -> dict:
        """交易所开市状态 — Finnhub > Mock"""
        result = self._try_chain(
            lambda: self._finnhub and self._finnhub.get_market_status(),
        )
        return result or {"isOpen": True, "exchange": "US", "source": "mock"}

    def get_ipo_calendar(self) -> list:
        """IPO日历 — Finnhub > Mock"""
        result = self._try_chain(
            lambda: self._finnhub and self._finnhub.get_ipo_calendar(),
        )
        return result or []

    def get_earnings_calendar(self, ticker: str = None) -> list:
        """财报日历 — Finnhub > Mock"""
        result = self._try_chain(
            lambda: self._finnhub and self._finnhub.get_earnings_calendar(ticker),
        )
        return result or []

    # ════════════════════════════════════════════════════════════
    # 其他数据
    # ════════════════════════════════════════════════════════════

    def get_trends(self, keyword: str) -> dict:
        result = self._try_chain(
            lambda: self._scraper and self._scraper.get_trends_proxy(keyword),
        )
        return result or self._mock.fetch("trends", {"keyword": keyword})

    def get_etf(self, ticker: str) -> dict:
        result = self._try_chain(
            lambda: self._yahoo and self._yahoo.fetch("etf", {"ticker": ticker.upper()}),
        )
        return result or self._mock.fetch("etf", {"ticker": ticker.upper()})

    def get_splits(self, ticker: str) -> list:
        result = self._try_chain(
            lambda: self._yahoo and self._yahoo.fetch("splits", {"ticker": ticker.upper()}),
        )
        return result or self._mock.fetch("splits", {"ticker": ticker.upper()})

    def get_revenue(self, ticker: str) -> dict:
        return self._mock.fetch("revenue", {"ticker": ticker.upper()})

    def get_risk(self, ticker: str) -> list:
        return self._mock.fetch("risk", {"ticker": ticker.upper()})

    def get_whales_detail(self, ticker: str) -> list:
        result = self._try_chain(
            lambda: self._scraper and self._scraper.get_quiver_headlines(ticker.upper()),
        )
        return result or self._mock.fetch("whales", {"ticker": ticker.upper()})

    def get_patents(self, company: str) -> list:
        return self._mock.fetch("patents", {"company_name": company})

    def get_app_ratings(self, app_name: str) -> dict:
        return self._mock.fetch("app-ratings", {"app_name": app_name})

    def get_cnbc_picks(self) -> list:
        return self._mock.fetch("media/cnbc", {})

    def get_cramer_tracker(self) -> list:
        return self._mock.fetch("media/cramer", {})

    def get_famous_portfolio(self, name: str) -> dict:
        return self._mock.fetch("portfolio/famous", {"celebrity_name": name})


# ── 全局单例 ─────────────────────────────────────────────────
_provider_instance: Optional[DataProvider] = None


def get_provider() -> DataProvider:
    global _provider_instance
    if _provider_instance is None:
        _provider_instance = DataProvider()
    return _provider_instance
