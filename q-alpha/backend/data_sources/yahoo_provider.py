"""
Yahoo Finance Data Provider
Uses yfinance library (no API key required).
"""

import logging
from typing import Any, Optional


logger = logging.getLogger("q-alpha.yahoo")


class YahooProvider:
    name = "yahoo"

    def is_available(self) -> bool:
        try:
            import yfinance
            return True
        except ImportError:
            return False

    def fetch(self, endpoint: str, params: dict) -> Optional[Any]:
        import yfinance as yf

        ticker_sym = params.get("ticker", "AAPL").upper()

        if endpoint == "stock/price":
            return self._get_price(ticker_sym)
        elif endpoint == "stock/candles":
            return self._get_candles(ticker_sym, params.get("timeframe", "1d"))
        elif endpoint == "stock/info":
            return self._get_info(ticker_sym)
        elif endpoint == "market/popular":
            return self._get_popular()
        elif endpoint == "etf":
            return self._get_etf(ticker_sym)
        elif endpoint == "splits":
            return self._get_splits(ticker_sym)
        return None

    def _get_price(self, ticker: str) -> dict:
        import yfinance as yf
        t = yf.Ticker(ticker)
        info = t.fast_info
        hist = t.history(period="2d")
        if hist.empty:
            return None
        current = float(hist["Close"].iloc[-1])
        prev = float(hist["Close"].iloc[-2]) if len(hist) > 1 else current
        change = current - prev
        change_pct = (change / prev * 100) if prev != 0 else 0
        volume = int(hist["Volume"].iloc[-1])
        return {
            "ticker": ticker,
            "price": round(current, 2),
            "change": round(change, 2),
            "change_pct": round(change_pct, 2),
            "volume": volume,
            "market_cap": getattr(info, "market_cap", None),
            "source": "yahoo",
        }

    def _get_candles(self, ticker: str, timeframe: str) -> dict:
        import yfinance as yf
        period_map = {
            "1d": ("1d", "5m"),
            "5d": ("5d", "15m"),
            "1mo": ("1mo", "1h"),
            "3mo": ("3mo", "1d"),
            "6mo": ("6mo", "1d"),
            "1y": ("1y", "1d"),
            "5y": ("5y", "1wk"),
        }
        period, interval = period_map.get(timeframe, ("3mo", "1d"))
        t = yf.Ticker(ticker)
        hist = t.history(period=period, interval=interval)
        if hist.empty:
            return None
        candles = []
        for idx, row in hist.iterrows():
            candles.append({
                "time": int(idx.timestamp() * 1000),
                "open": round(float(row["Open"]), 2),
                "high": round(float(row["High"]), 2),
                "low": round(float(row["Low"]), 2),
                "close": round(float(row["Close"]), 2),
                "volume": int(row["Volume"]),
            })
        return {"ticker": ticker, "timeframe": timeframe, "candles": candles}

    def _get_info(self, ticker: str) -> dict:
        import yfinance as yf
        t = yf.Ticker(ticker)
        info = t.info
        return {
            "ticker": ticker,
            "name": info.get("longName", ticker),
            "sector": info.get("sector", ""),
            "industry": info.get("industry", ""),
            "description": info.get("longBusinessSummary", ""),
            "employees": info.get("fullTimeEmployees"),
            "website": info.get("website", ""),
            "pe_ratio": info.get("trailingPE"),
            "eps": info.get("trailingEps"),
            "dividend_yield": info.get("dividendYield"),
            "52w_high": info.get("fiftyTwoWeekHigh"),
            "52w_low": info.get("fiftyTwoWeekLow"),
            "avg_volume": info.get("averageVolume"),
            "beta": info.get("beta"),
            "market_cap": info.get("marketCap"),
        }

    def _get_popular(self) -> list:
        import yfinance as yf
        tickers = ["AAPL", "TSLA", "NVDA", "MSFT", "GOOGL", "AMZN", "META", "AMD"]
        results = []
        for sym in tickers:
            try:
                price_data = self._get_price(sym)
                if price_data:
                    results.append(price_data)
            except Exception:
                pass
        return results

    def _get_etf(self, ticker: str) -> dict:
        import yfinance as yf
        t = yf.Ticker(ticker)
        holdings = []
        try:
            df = t.get_holdings()
            if df is not None and not df.empty:
                for _, row in df.iterrows():
                    holdings.append({
                        "symbol": row.get("Symbol", ""),
                        "holding_percent": row.get("Holding Percent", 0),
                    })
        except Exception:
            pass
        return {"ticker": ticker, "holdings": holdings}

    def _get_splits(self, ticker: str) -> list:
        import yfinance as yf
        t = yf.Ticker(ticker)
        splits = t.splits
        result = []
        for date, ratio in splits.items():
            result.append({
                "date": str(date.date()),
                "ratio": float(ratio),
            })
        return result
