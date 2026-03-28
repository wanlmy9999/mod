"""
AkShare 数据提供商（美股）
优先用于在第三方 API 不可用时补充行情与K线数据。
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Optional

logger = logging.getLogger("q-alpha.akshare")


class AkShareProvider:
    name = "akshare"

    def __init__(self):
        self._ak = None
        try:
            import akshare as ak  # type: ignore
            self._ak = ak
        except Exception as e:
            logger.warning(f"AkShare not available: {e}")

    def is_available(self) -> bool:
        return self._ak is not None

    def get_quote(self, symbol: str) -> Optional[dict]:
        """尝试使用 AkShare 获取美股快照。"""
        if not self._ak:
            return None
        try:
            df = self._ak.stock_us_spot_em()
            if df is None or df.empty:
                return None

            candidates = ["代码", "symbol", "代码(symbol)", "名称"]
            code_col = next((c for c in candidates if c in df.columns), None)
            if not code_col:
                code_col = df.columns[0]

            target = symbol.upper()
            row = None
            for _, r in df.iterrows():
                code = str(r.get(code_col, "")).upper()
                if target in code or code.endswith(target):
                    row = r
                    break
            if row is None:
                return None

            def pick(*cols, default=0):
                for c in cols:
                    if c in df.columns:
                        v = row.get(c)
                        if v is not None and str(v) != "nan":
                            return v
                return default

            price = float(pick("最新价", "最新", "price", default=0))
            prev_close = float(pick("昨收", "昨收价", "prev_close", default=0))
            change = price - prev_close if prev_close else float(pick("涨跌额", "change", default=0))
            change_pct = (
                (change / prev_close * 100) if prev_close else float(pick("涨跌幅", "change_pct", default=0))
            )
            return {
                "ticker": target,
                "name": str(pick("名称", "name", default=target)),
                "price": round(price, 2),
                "change": round(change, 2),
                "change_pct": round(change_pct, 2),
                "open": float(pick("今开", "open", default=0)),
                "high": float(pick("最高", "high", default=0)),
                "low": float(pick("最低", "low", default=0)),
                "prev_close": round(prev_close, 2) if prev_close else None,
                "volume": int(float(pick("成交量", "volume", default=0))),
                "source": "akshare",
            }
        except Exception as e:
            logger.warning(f"AkShare get_quote failed for {symbol}: {e}")
            return None

    def get_candles(self, symbol: str, timeframe: str = "3mo") -> Optional[dict]:
        """尝试使用 AkShare 获取美股历史K线。"""
        if not self._ak:
            return None

        days_map = {"1d": 2, "5d": 7, "1mo": 35, "3mo": 120, "6mo": 220, "1y": 380, "5y": 1900}
        days = days_map.get(timeframe, 120)
        start_date = (datetime.utcnow() - timedelta(days=days)).strftime("%Y%m%d")
        end_date = datetime.utcnow().strftime("%Y%m%d")

        try:
            # AkShare 美股历史接口常见 symbol 形态示例：105.AAPL
            ak_symbol = f"105.{symbol.upper()}"
            df = self._ak.stock_us_hist(
                symbol=ak_symbol, period="daily", start_date=start_date, end_date=end_date, adjust=""
            )
            if df is None or df.empty:
                return None

            candles = []
            for _, r in df.iterrows():
                date_raw = r.get("日期") or r.get("date")
                dt = datetime.strptime(str(date_raw)[:10], "%Y-%m-%d")
                candles.append(
                    {
                        "time": int(dt.timestamp() * 1000),
                        "open": round(float(r.get("开盘", r.get("open", 0))), 2),
                        "high": round(float(r.get("最高", r.get("high", 0))), 2),
                        "low": round(float(r.get("最低", r.get("low", 0))), 2),
                        "close": round(float(r.get("收盘", r.get("close", 0))), 2),
                        "volume": int(float(r.get("成交量", r.get("volume", 0)) or 0)),
                    }
                )
            return {"ticker": symbol.upper(), "timeframe": timeframe, "candles": candles}
        except Exception as e:
            logger.warning(f"AkShare get_candles failed for {symbol}: {e}")
            return None
