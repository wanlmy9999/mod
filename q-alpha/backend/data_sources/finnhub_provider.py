"""
Finnhub 数据提供商
API Key: d6tp7hpr01qhkb4531f0d6tp7hpr01qhkb4531fg
文档: https://finnhub.io/docs/api
支持: 实时报价/K线/公司信息/分析师/内幕交易/国会交易/新闻/财务指标/情绪
"""

import logging
import requests
from typing import Any, Optional
from datetime import datetime, timedelta
import os

logger = logging.getLogger("q-alpha.finnhub")

FINNHUB_BASE = "https://finnhub.io/api/v1"
FINNHUB_KEY  = os.getenv("FINNHUB_API_KEY", "d73m2ghr01qjjol3gt4gd73m2ghr01qjjol3gt50")


def _get(path: str, params: dict) -> Optional[dict]:
    """发起 Finnhub GET 请求，自动添加 token"""
    try:
        params["token"] = FINNHUB_KEY
        resp = requests.get(f"{FINNHUB_BASE}{path}", params=params, timeout=8)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.RequestException as e:
        logger.warning(f"Finnhub {path} 请求失败: {e}")
        return None


class FinnhubProvider:
    """Finnhub 数据提供商 — 14个API端点"""

    name = "finnhub"

    def is_available(self) -> bool:
        return bool(FINNHUB_KEY)

    # ── 1. 实时报价 ──────────────────────────────────────────
    def get_quote(self, symbol: str) -> Optional[dict]:
        """
        GET /quote?symbol=AAPL&token=KEY
        响应: c(现价) d(涨跌额) dp(涨跌%) h(最高) l(最低) o(开盘) pc(昨收) t(时间戳)
        """
        data = _get("/quote", {"symbol": symbol.upper()})
        if not data or data.get("c") is None:
            return None
        return {
            "ticker":     symbol.upper(),
            "price":      round(float(data.get("c", 0)), 2),
            "change":     round(float(data.get("d", 0)), 2),
            "change_pct": round(float(data.get("dp", 0)), 2),
            "high":       data.get("h"),
            "low":        data.get("l"),
            "open":       data.get("o"),
            "prev_close": data.get("pc"),
            "timestamp":  data.get("t"),
            "source":     "finnhub",
        }

    # ── 2. K线数据 ──────────────────────────────────────────
    def get_candles(self, symbol: str, timeframe: str = "3mo") -> Optional[dict]:
        """
        GET /stock/candle?symbol=AAPL&resolution=D&from=TS&to=TS&token=KEY
        resolution: 1/5/15/30/60/D/W/M
        响应: o(开) h(高) l(低) c(收) v(量) t(时间戳数组) s(ok/no_data)
        """
        period_map = {
            "1d":  (1,    "5"),
            "5d":  (5,    "15"),
            "1mo": (30,   "60"),
            "3mo": (90,   "D"),
            "6mo": (180,  "D"),
            "1y":  (365,  "D"),
            "5y":  (1825, "W"),
        }
        days, resolution = period_map.get(timeframe, (90, "D"))
        now = int(datetime.utcnow().timestamp())
        frm = int((datetime.utcnow() - timedelta(days=days)).timestamp())

        data = _get("/stock/candle", {
            "symbol": symbol.upper(),
            "resolution": resolution,
            "from": frm,
            "to": now,
        })
        if not data or data.get("s") == "no_data" or not data.get("c"):
            return None

        candles = []
        for i in range(len(data["c"])):
            candles.append({
                "time":   data["t"][i] * 1000,
                "open":   round(data["o"][i], 2),
                "high":   round(data["h"][i], 2),
                "low":    round(data["l"][i], 2),
                "close":  round(data["c"][i], 2),
                "volume": data["v"][i],
            })
        return {"ticker": symbol.upper(), "timeframe": timeframe, "candles": candles}

    # ── 3. 公司基本信息 ──────────────────────────────────────
    def get_profile(self, symbol: str) -> Optional[dict]:
        """
        GET /stock/profile2?symbol=AAPL&token=KEY
        响应: name,ticker,finnhubIndustry,marketCapitalization,shareOutstanding,
               country,currency,exchange,ipo,logo,phone,weburl
        """
        data = _get("/stock/profile2", {"symbol": symbol.upper()})
        if not data:
            return None
        return {
            "ticker":      symbol.upper(),
            "name":        data.get("name", symbol),
            "sector":      data.get("finnhubIndustry", ""),
            "industry":    data.get("finnhubIndustry", ""),
            "market_cap":  (data.get("marketCapitalization") or 0) * 1e6,
            "shares":      data.get("shareOutstanding"),
            "country":     data.get("country"),
            "currency":    data.get("currency"),
            "exchange":    data.get("exchange"),
            "ipo_date":    data.get("ipo"),
            "logo":        data.get("logo"),
            "phone":       data.get("phone"),
            "website":     data.get("weburl"),
        }

    # ── 4. 分析师评级 ──────────────────────────────────────
    def get_recommendations(self, symbol: str) -> Optional[list]:
        """
        GET /stock/recommendation?symbol=AAPL&token=KEY
        响应数组: period,strongBuy,buy,hold,sell,strongSell
        """
        data = _get("/stock/recommendation", {"symbol": symbol.upper()})
        if not data or not isinstance(data, list):
            return None
        results = []
        for entry in data[:3]:  # 最近3个月
            total = sum([
                entry.get("strongBuy", 0), entry.get("buy", 0),
                entry.get("hold", 0), entry.get("sell", 0), entry.get("strongSell", 0)
            ])
            if total == 0:
                continue
            buy_pct = (entry.get("strongBuy", 0) + entry.get("buy", 0)) / total * 100
            results.append({
                "period":     entry.get("period"),
                "strong_buy": entry.get("strongBuy", 0),
                "buy":        entry.get("buy", 0),
                "hold":       entry.get("hold", 0),
                "sell":       entry.get("sell", 0),
                "strong_sell":entry.get("strongSell", 0),
                "total":      total,
                "buy_pct":    round(buy_pct, 1),
                "rating":     "Buy" if buy_pct >= 60 else "Hold" if buy_pct >= 40 else "Sell",
                "firm":       "华尔街一致预期",
                "source":     "finnhub",
            })
        return results if results else None

    # ── 5. 内幕交易 ─────────────────────────────────────────
    def get_insider_transactions(self, symbol: str) -> Optional[list]:
        """
        GET /stock/insider-transactions?symbol=AAPL&token=KEY
        响应: data[].name,share,change,transactionDate,transactionCode,transactionPrice
        transactionCode: P=买入 S=卖出 A=授予 D=处置
        """
        data = _get("/stock/insider-transactions", {"symbol": symbol.upper()})
        if not data or not data.get("data"):
            return None
        code_map = {"P": "Purchase", "S": "Sale", "A": "Award", "D": "Dispose"}
        results = []
        for t in data["data"][:20]:
            code = t.get("transactionCode", "")
            action = code_map.get(code, code)
            shares = abs(t.get("change", 0))
            price  = t.get("transactionPrice", 0) or 0
            amount = shares * price
            results.append({
                "insider_name": t.get("name", "—"),
                "role":         t.get("position", "高管"),
                "action":       action,
                "shares":       shares,
                "price":        round(price, 2),
                "amount":       f"${amount/1e6:.1f}M" if amount > 1e6 else f"${amount/1e3:.0f}K",
                "date":         t.get("transactionDate", ""),
                "ticker":       symbol.upper(),
                "source":       "finnhub",
            })
        return results if results else None

    # ── 6. 公司新闻 ──────────────────────────────────────────
    def get_news(self, symbol: str) -> Optional[list]:
        """
        GET /company-news?symbol=AAPL&from=2024-01-01&to=2024-12-31&token=KEY
        响应: category,datetime,headline,id,image,related,source,summary,url
        """
        from datetime import date
        today = date.today()
        frm = (today - timedelta(days=30)).strftime("%Y-%m-%d")
        to  = today.strftime("%Y-%m-%d")
        data = _get("/company-news", {
            "symbol": symbol.upper(),
            "from": frm,
            "to": to,
        })
        if not data or not isinstance(data, list):
            return None
        results = []
        for item in data[:10]:
            results.append({
                "title":    item.get("headline", ""),
                "summary":  item.get("summary", ""),
                "category": item.get("category", "general"),
                "source":   item.get("source", ""),
                "url":      item.get("url", ""),
                "time":     str(item.get("datetime", "")),
            })
        return results if results else None

    # ── 7. 财务指标 ─────────────────────────────────────────
    def get_metrics(self, symbol: str) -> Optional[dict]:
        """
        GET /stock/metric?symbol=AAPL&metric=all&token=KEY
        响应: metric.{peNormalizedAnnual,epsNormalizedAnnual,revenuePerShareAnnual,
               roaRfy,roeRfy,currentRatioAnnual,quickRatioAnnual,debtToEquityAnnual}
        """
        data = _get("/stock/metric", {"symbol": symbol.upper(), "metric": "all"})
        if not data or not data.get("metric"):
            return None
        m = data["metric"]
        return {
            "ticker":          symbol.upper(),
            "pe_ratio":        m.get("peNormalizedAnnual"),
            "eps":             m.get("epsNormalizedAnnual"),
            "revenue_ps":      m.get("revenuePerShareAnnual"),
            "roa":             m.get("roaRfy"),
            "roe":             m.get("roeRfy"),
            "current_ratio":   m.get("currentRatioAnnual"),
            "quick_ratio":     m.get("quickRatioAnnual"),
            "debt_to_equity":  m.get("debtToEquityAnnual"),
            "52w_high":        m.get("52WeekHigh"),
            "52w_low":         m.get("52WeekLow"),
            "beta":            m.get("beta"),
            "dividend_yield":  m.get("dividendYieldIndicatedAnnual"),
            "source":          "finnhub",
        }

    # ── 8. 情绪分析 ─────────────────────────────────────────
    def get_sentiment(self, symbol: str) -> Optional[dict]:
        """
        GET /news-sentiment?symbol=AAPL&token=KEY
        响应: companyNewsScore,sectorAverageBullishPercent,sectorAverageNewsScore,
               sentiment.bullishPercent,sentiment.bearishPercent
        """
        data = _get("/news-sentiment", {"symbol": symbol.upper()})
        if not data:
            return None
        sentiment = data.get("sentiment", {})
        return {
            "ticker":          symbol.upper(),
            "news_score":      data.get("companyNewsScore"),
            "sector_avg":      data.get("sectorAverageNewsScore"),
            "bullish_pct":     sentiment.get("bullishPercent"),
            "bearish_pct":     sentiment.get("bearishPercent"),
            "source":          "finnhub",
        }

    # ── 9. 国会交易 ─────────────────────────────────────────
    def get_congressional_trading(self, symbol: str) -> Optional[list]:
        """
        GET /stock/congressional-trading?symbol=AAPL&token=KEY
        响应: congressionalTrading[].name,action,amount,date,party,reportDate,ticker
        """
        data = _get("/stock/congressional-trading", {"symbol": symbol.upper()})
        if not data or not data.get("congressionalTrading"):
            return None
        results = []
        for t in data["congressionalTrading"][:20]:
            results.append({
                "politician": t.get("name", ""),
                "party":      t.get("party", ""),
                "ticker":     t.get("ticker", symbol.upper()),
                "action":     "Purchase" if t.get("action","").lower() in ("buy","purchase") else "Sale",
                "amount":     t.get("amount", ""),
                "date":       t.get("date", ""),
                "report_date":t.get("reportDate", ""),
                "source":     "finnhub",
            })
        return results if results else None

    # ── 10. 同行业对标 ──────────────────────────────────────
    def get_peers(self, symbol: str) -> Optional[list]:
        """
        GET /stock/peers?symbol=AAPL&token=KEY
        响应: [ticker字符串数组]
        """
        data = _get("/stock/peers", {"symbol": symbol.upper()})
        return data if data and isinstance(data, list) else None

    # ── 11. 财报日历 ────────────────────────────────────────
    def get_earnings_calendar(self, symbol: str = None) -> Optional[list]:
        """
        GET /calendar/earnings?from=YYYY-MM-DD&to=YYYY-MM-DD&symbol=AAPL&token=KEY
        响应: earningsCalendar[].symbol,date,epsEstimate,epsActual,quarter,year
        """
        from datetime import date
        today = date.today()
        frm = today.strftime("%Y-%m-%d")
        to  = (today + timedelta(days=90)).strftime("%Y-%m-%d")
        params = {"from": frm, "to": to}
        if symbol:
            params["symbol"] = symbol.upper()
        data = _get("/calendar/earnings", params)
        cal = (data or {}).get("earningsCalendar", [])
        return cal[:20] if cal else None

    # ── 12. 内幕情绪汇总 ────────────────────────────────────
    def get_insider_sentiment(self, symbol: str) -> Optional[list]:
        """
        GET /stock/insider-sentiment?symbol=AAPL&from=2023-01-01&to=2024-12-31&token=KEY
        响应: data[].change,month,mspr(月度净买入评分),purchase,sales,symbol,year
        mspr > 0 表示净买入，< 0 表示净卖出
        """
        from datetime import date
        today = date.today()
        frm = f"{today.year - 1}-01-01"
        to  = today.strftime("%Y-%m-%d")
        data = _get("/stock/insider-sentiment", {
            "symbol": symbol.upper(),
            "from": frm,
            "to": to,
        })
        if not data or not data.get("data"):
            return None
        return data["data"][:12]

    # ── 13. 市场状态 ────────────────────────────────────────
    def get_market_status(self) -> Optional[dict]:
        """
        GET /stock/market-status?exchange=US&token=KEY
        响应: exchange,holiday,isOpen,session,timezone,t
        """
        return _get("/stock/market-status", {"exchange": "US"})

    # ── 14. IPO日历 ─────────────────────────────────────────
    def get_ipo_calendar(self) -> Optional[list]:
        """
        GET /calendar/ipo?from=YYYY-MM-DD&to=YYYY-MM-DD&token=KEY
        响应: ipoCalendar[].symbol,name,date,price,status,shares
        """
        from datetime import date
        today = date.today()
        frm = today.strftime("%Y-%m-%d")
        to  = (today + timedelta(days=90)).strftime("%Y-%m-%d")
        data = _get("/calendar/ipo", {"from": frm, "to": to})
        cal = (data or {}).get("ipoCalendar", [])
        return cal[:20] if cal else None
