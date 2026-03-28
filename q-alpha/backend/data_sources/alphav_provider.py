"""
Alpha Vantage 数据提供商
API Key: N21EBMG315OFXTXB
文档: https://www.alphavantage.co/documentation/
支持: 股票报价/K线/基本面/财报/技术指标(RSI/MACD/SMA/EMA)/新闻情绪
注意: 免费版每分钟5次请求，每日500次
"""

import logging
import requests
from typing import Any, Optional

logger = logging.getLogger("q-alpha.alphav")

ALPHAV_BASE = "https://www.alphavantage.co/query"
ALPHAV_KEY  = "N21EBMG315OFXTXB"


def _get(params: dict) -> Optional[dict]:
    """发起 Alpha Vantage GET 请求，自动添加 apikey"""
    try:
        params["apikey"] = ALPHAV_KEY
        resp = requests.get(ALPHAV_BASE, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        # 检查是否触发频率限制
        if "Note" in data or "Information" in data:
            logger.warning(f"Alpha Vantage 频率限制: {data.get('Note') or data.get('Information')}")
            return None
        return data
    except requests.exceptions.RequestException as e:
        logger.warning(f"Alpha Vantage 请求失败: {e}")
        return None


class AlphaVantageProvider:
    """Alpha Vantage 数据提供商 — 13个API端点"""

    name = "alpha_vantage"

    def is_available(self) -> bool:
        return bool(ALPHAV_KEY)

    # ── 1. 实时报价 ─────────────────────────────────────────
    def get_quote(self, symbol: str) -> Optional[dict]:
        """
        function=GLOBAL_QUOTE&symbol=AAPL&apikey=KEY
        响应: Global Quote.{
          "01. symbol": "AAPL",
          "05. price": "189.5000",
          "09. change": "1.2300",
          "10. change percent": "0.6536%",
          "06. volume": "52345678",
          "07. latest trading day": "2024-01-15",
          "02. open": "188.20",
          "03. high": "190.10",
          "04. low": "187.80",
          "08. previous close": "188.27"
        }
        """
        data = _get({"function": "GLOBAL_QUOTE", "symbol": symbol.upper()})
        if not data:
            return None
        q = data.get("Global Quote", {})
        if not q.get("05. price"):
            return None
        pct_str = q.get("10. change percent", "0%").replace("%", "")
        return {
            "ticker":     symbol.upper(),
            "price":      round(float(q.get("05. price", 0)), 2),
            "change":     round(float(q.get("09. change", 0)), 2),
            "change_pct": round(float(pct_str), 2),
            "volume":     int(q.get("06. volume", 0)),
            "open":       float(q.get("02. open", 0)),
            "high":       float(q.get("03. high", 0)),
            "low":        float(q.get("04. low", 0)),
            "prev_close": float(q.get("08. previous close", 0)),
            "trade_date": q.get("07. latest trading day"),
            "source":     "alpha_vantage",
        }

    # ── 2. 日K线 ────────────────────────────────────────────
    def get_daily_candles(self, symbol: str, full: bool = False) -> Optional[dict]:
        """
        function=TIME_SERIES_DAILY&symbol=AAPL&outputsize=compact|full&apikey=KEY
        compact=最近100条, full=完整20年历史
        响应: Time Series (Daily).{日期: {1.open,2.high,3.low,4.close,5.volume}}
        """
        data = _get({
            "function": "TIME_SERIES_DAILY",
            "symbol": symbol.upper(),
            "outputsize": "full" if full else "compact",
        })
        if not data:
            return None
        ts = data.get("Time Series (Daily)", {})
        if not ts:
            return None
        candles = []
        for date_str, vals in sorted(ts.items())[-200:]:
            try:
                import datetime
                dt = datetime.datetime.strptime(date_str, "%Y-%m-%d")
                candles.append({
                    "time":   int(dt.timestamp() * 1000),
                    "open":   round(float(vals["1. open"]), 2),
                    "high":   round(float(vals["2. high"]), 2),
                    "low":    round(float(vals["3. low"]), 2),
                    "close":  round(float(vals["4. close"]), 2),
                    "volume": int(vals["5. volume"]),
                })
            except Exception:
                continue
        return {"ticker": symbol.upper(), "candles": candles} if candles else None

    # ── 3. 公司基本面 ────────────────────────────────────────
    def get_overview(self, symbol: str) -> Optional[dict]:
        """
        function=OVERVIEW&symbol=AAPL&apikey=KEY
        响应字段(重要): Symbol,Name,Description,Exchange,Country,Sector,Industry,
          MarketCapitalization,PERatio,EPS,DividendYield,52WeekHigh,52WeekLow,
          Beta,EVToEBITDA,ProfitMargin,OperatingMarginTTM,ReturnOnEquityTTM,
          RevenuePerShareTTM,QuarterlyEarningsGrowthYOY,SharesOutstanding
        """
        data = _get({"function": "OVERVIEW", "symbol": symbol.upper()})
        if not data or not data.get("Symbol"):
            return None
        return {
            "ticker":         data.get("Symbol", symbol.upper()),
            "name":           data.get("Name", symbol),
            "description":    data.get("Description", ""),
            "exchange":       data.get("Exchange", ""),
            "country":        data.get("Country", "US"),
            "sector":         data.get("Sector", ""),
            "industry":       data.get("Industry", ""),
            "market_cap":     float(data.get("MarketCapitalization") or 0),
            "pe_ratio":       float(data.get("PERatio") or 0) or None,
            "eps":            float(data.get("EPS") or 0) or None,
            "dividend_yield": float(data.get("DividendYield") or 0) or None,
            "52w_high":       float(data.get("52WeekHigh") or 0) or None,
            "52w_low":        float(data.get("52WeekLow") or 0) or None,
            "beta":           float(data.get("Beta") or 0) or None,
            "profit_margin":  data.get("ProfitMargin"),
            "roe":            data.get("ReturnOnEquityTTM"),
            "revenue_ps":     data.get("RevenuePerShareTTM"),
            "shares":         data.get("SharesOutstanding"),
            "employees":      data.get("FullTimeEmployees"),
            "website":        "",
            "source":         "alpha_vantage",
        }

    # ── 4. 利润表 ────────────────────────────────────────────
    def get_income_statement(self, symbol: str) -> Optional[dict]:
        """
        function=INCOME_STATEMENT&symbol=AAPL&apikey=KEY
        响应: annualReports[].{fiscalDateEnding,totalRevenue,grossProfit,
          operatingIncome,netIncome,ebitda,eps,ebitdaRatio}
        """
        data = _get({"function": "INCOME_STATEMENT", "symbol": symbol.upper()})
        if not data or not data.get("annualReports"):
            return None
        reports = []
        for r in data["annualReports"][:4]:
            reports.append({
                "period":           r.get("fiscalDateEnding"),
                "total_revenue":    float(r.get("totalRevenue") or 0),
                "gross_profit":     float(r.get("grossProfit") or 0),
                "operating_income": float(r.get("operatingIncome") or 0),
                "net_income":       float(r.get("netIncome") or 0),
                "ebitda":           float(r.get("ebitda") or 0),
                "eps":              float(r.get("reportedEPS") or 0),
            })
        return {"ticker": symbol.upper(), "annual_reports": reports} if reports else None

    # ── 5. 资产负债表 ────────────────────────────────────────
    def get_balance_sheet(self, symbol: str) -> Optional[dict]:
        """
        function=BALANCE_SHEET&symbol=AAPL&apikey=KEY
        响应: annualReports[].{totalAssets,totalLiabilities,totalShareholderEquity,
          cashAndCashEquivalentsAtCarryingValue,longTermDebtNoncurrent}
        """
        data = _get({"function": "BALANCE_SHEET", "symbol": symbol.upper()})
        if not data or not data.get("annualReports"):
            return None
        reports = []
        for r in data["annualReports"][:4]:
            reports.append({
                "period":     r.get("fiscalDateEnding"),
                "assets":     float(r.get("totalAssets") or 0),
                "liabilities":float(r.get("totalLiabilities") or 0),
                "equity":     float(r.get("totalShareholderEquity") or 0),
                "cash":       float(r.get("cashAndCashEquivalentsAtCarryingValue") or 0),
                "long_term_debt": float(r.get("longTermDebtNoncurrent") or 0),
            })
        return {"ticker": symbol.upper(), "annual_reports": reports} if reports else None

    # ── 6. 现金流量表 ────────────────────────────────────────
    def get_cash_flow(self, symbol: str) -> Optional[dict]:
        """
        function=CASH_FLOW&symbol=AAPL&apikey=KEY
        响应: annualReports[].{operatingCashflow,capitalExpenditures,
          dividendPayout,freeCashFlow,changeInCashAndCashEquivalents}
        """
        data = _get({"function": "CASH_FLOW", "symbol": symbol.upper()})
        if not data or not data.get("annualReports"):
            return None
        reports = []
        for r in data["annualReports"][:4]:
            op_cf = float(r.get("operatingCashflow") or 0)
            capex = float(r.get("capitalExpenditures") or 0)
            reports.append({
                "period":       r.get("fiscalDateEnding"),
                "operating_cf": op_cf,
                "capex":        capex,
                "free_cf":      op_cf - capex,
                "dividends":    float(r.get("dividendPayout") or 0),
            })
        return {"ticker": symbol.upper(), "annual_reports": reports} if reports else None

    # ── 7. 季度EPS ───────────────────────────────────────────
    def get_earnings(self, symbol: str) -> Optional[dict]:
        """
        function=EARNINGS&symbol=AAPL&apikey=KEY
        响应: quarterlyEarnings[].{fiscalDateEnding,reportedEPS,estimatedEPS,
          surprise,surprisePercentage,reportedDate}
        """
        data = _get({"function": "EARNINGS", "symbol": symbol.upper()})
        if not data or not data.get("quarterlyEarnings"):
            return None
        quarters = []
        for q in data["quarterlyEarnings"][:8]:
            quarters.append({
                "period":      q.get("fiscalDateEnding"),
                "reported_eps":float(q.get("reportedEPS") or 0),
                "estimated_eps":float(q.get("estimatedEPS") or 0),
                "surprise":    float(q.get("surprise") or 0),
                "surprise_pct":float(q.get("surprisePercentage") or 0),
                "report_date": q.get("reportedDate"),
            })
        return {"ticker": symbol.upper(), "quarterly_earnings": quarters} if quarters else None

    # ── 8. RSI 指标 ──────────────────────────────────────────
    def get_rsi(self, symbol: str, period: int = 14) -> Optional[dict]:
        """
        function=RSI&symbol=AAPL&interval=daily&time_period=14&series_type=close&apikey=KEY
        响应: Technical Analysis: RSI.{日期: {RSI: "值"}}
        """
        data = _get({
            "function":    "RSI",
            "symbol":      symbol.upper(),
            "interval":    "daily",
            "time_period": period,
            "series_type": "close",
        })
        if not data:
            return None
        ts = data.get("Technical Analysis: RSI", {})
        if not ts:
            return None
        # 取最新值
        latest_date = sorted(ts.keys())[-1]
        return {
            "ticker":  symbol.upper(),
            "rsi":     round(float(ts[latest_date]["RSI"]), 2),
            "date":    latest_date,
            "period":  period,
            "source":  "alpha_vantage",
        }

    # ── 9. MACD 指标 ─────────────────────────────────────────
    def get_macd(self, symbol: str) -> Optional[dict]:
        """
        function=MACD&symbol=AAPL&interval=daily&series_type=close&apikey=KEY
        响应: Technical Analysis: MACD.{日期: {MACD,MACD_Signal,MACD_Hist}}
        """
        data = _get({
            "function":    "MACD",
            "symbol":      symbol.upper(),
            "interval":    "daily",
            "series_type": "close",
        })
        if not data:
            return None
        ts = data.get("Technical Analysis: MACD", {})
        if not ts:
            return None
        latest_date = sorted(ts.keys())[-1]
        d = ts[latest_date]
        return {
            "ticker":    symbol.upper(),
            "macd":      round(float(d.get("MACD", 0)), 4),
            "signal":    round(float(d.get("MACD_Signal", 0)), 4),
            "histogram": round(float(d.get("MACD_Hist", 0)), 4),
            "date":      latest_date,
            "source":    "alpha_vantage",
        }

    # ── 10. SMA 移动平均 ─────────────────────────────────────
    def get_sma(self, symbol: str, period: int = 50) -> Optional[dict]:
        """
        function=SMA&symbol=AAPL&interval=daily&time_period=50&series_type=close&apikey=KEY
        响应: Technical Analysis: SMA.{日期: {SMA: "值"}}
        """
        data = _get({
            "function":    "SMA",
            "symbol":      symbol.upper(),
            "interval":    "daily",
            "time_period": period,
            "series_type": "close",
        })
        if not data:
            return None
        ts = data.get("Technical Analysis: SMA", {})
        if not ts:
            return None
        latest_date = sorted(ts.keys())[-1]
        return {
            "ticker": symbol.upper(),
            "sma":    round(float(ts[latest_date]["SMA"]), 2),
            "period": period,
            "date":   latest_date,
            "source": "alpha_vantage",
        }

    # ── 11. EMA 指数移动平均 ─────────────────────────────────
    def get_ema(self, symbol: str, period: int = 20) -> Optional[dict]:
        """
        function=EMA&symbol=AAPL&interval=daily&time_period=20&series_type=close&apikey=KEY
        响应: Technical Analysis: EMA.{日期: {EMA: "值"}}
        """
        data = _get({
            "function":    "EMA",
            "symbol":      symbol.upper(),
            "interval":    "daily",
            "time_period": period,
            "series_type": "close",
        })
        if not data:
            return None
        ts = data.get("Technical Analysis: EMA", {})
        if not ts:
            return None
        latest_date = sorted(ts.keys())[-1]
        return {
            "ticker": symbol.upper(),
            "ema":    round(float(ts[latest_date]["EMA"]), 2),
            "period": period,
            "date":   latest_date,
            "source": "alpha_vantage",
        }

    # ── 12. 新闻情绪分析 ─────────────────────────────────────
    def get_news_sentiment(self, symbol: str) -> Optional[list]:
        """
        function=NEWS_SENTIMENT&tickers=AAPL&apikey=KEY
        可选参数: topics=financial_markets|technology|earnings
                 time_from=20240101T0000  time_to=20241231T2359
                 sort=LATEST|EARLIEST|RELEVANCE  limit=50
        响应: feed[].{title,url,source,time_published,
          overall_sentiment_score,overall_sentiment_label,
          ticker_sentiment[].{ticker,relevance_score,ticker_sentiment_score,ticker_sentiment_label}}
        情绪标签: Bullish/Somewhat-Bullish/Neutral/Somewhat-Bearish/Bearish
        """
        data = _get({
            "function": "NEWS_SENTIMENT",
            "tickers":  symbol.upper(),
            "sort":     "LATEST",
            "limit":    "10",
        })
        if not data or not data.get("feed"):
            return None
        results = []
        for item in data["feed"][:10]:
            results.append({
                "title":     item.get("title", ""),
                "source":    item.get("source", ""),
                "url":       item.get("url", ""),
                "time":      item.get("time_published", ""),
                "sentiment": item.get("overall_sentiment_label", "Neutral"),
                "score":     item.get("overall_sentiment_score", 0),
            })
        return results if results else None

    # ── 13. 分时K线 ──────────────────────────────────────────
    def get_intraday(self, symbol: str, interval: str = "5min") -> Optional[dict]:
        """
        function=TIME_SERIES_INTRADAY&symbol=AAPL&interval=5min&apikey=KEY
        interval: 1min/5min/15min/30min/60min
        响应: Time Series (5min).{时间: {1.open,2.high,3.low,4.close,5.volume}}
        """
        data = _get({
            "function": "TIME_SERIES_INTRADAY",
            "symbol":   symbol.upper(),
            "interval": interval,
        })
        if not data:
            return None
        key = f"Time Series ({interval})"
        ts = data.get(key, {})
        if not ts:
            return None
        candles = []
        import datetime
        for time_str, vals in sorted(ts.items())[-100:]:
            try:
                dt = datetime.datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
                candles.append({
                    "time":   int(dt.timestamp() * 1000),
                    "open":   round(float(vals["1. open"]), 2),
                    "high":   round(float(vals["2. high"]), 2),
                    "low":    round(float(vals["3. low"]), 2),
                    "close":  round(float(vals["4. close"]), 2),
                    "volume": int(vals["5. volume"]),
                })
            except Exception:
                continue
        return {"ticker": symbol.upper(), "interval": interval, "candles": candles} if candles else None

