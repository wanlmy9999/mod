"""
Tickdb 数据提供商
API Key: U1x4cW1qB0UtPkbNwmFxhRcYT79OZZea (有效期1个月)
文档: https://docs.tickdb.com
认证方式: Bearer Token (在请求头 Authorization: Bearer TOKEN 中传递)
Base URL: https://api.tickdb.com
注意: 到期后需要续期，到期前系统会自动回退到其他数据源
"""

import logging
import requests
from typing import Any, Optional

logger = logging.getLogger("q-alpha.tickdb")

TICKDB_BASE = "https://api.tickdb.com"
TICKDB_KEY  = "U1x4cW1qB0UtPkbNwmFxhRcYT79OZZea"


def _headers() -> dict:
    """生成认证头 — Tickdb 使用 Bearer Token"""
    return {
        "Authorization": f"Bearer {TICKDB_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


def _get(path: str, params: dict = None) -> Optional[Any]:
    """发起 Tickdb GET 请求"""
    try:
        resp = requests.get(
            f"{TICKDB_BASE}{path}",
            headers=_headers(),
            params=params or {},
            timeout=8,
        )
        if resp.status_code == 401:
            logger.error("Tickdb Token 已过期或无效，请更新 TICKDB_KEY")
            return None
        if resp.status_code == 429:
            logger.warning("Tickdb 请求频率超限，请稍后重试")
            return None
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.RequestException as e:
        logger.warning(f"Tickdb 请求失败 {path}: {e}")
        return None


class TickdbProvider:
    """
    Tickdb 数据提供商
    认证: Authorization: Bearer U1x4cW1qB0UtPkbNwmFxhRcYT79OZZea
    ⚠️ Token 有效期约1个月，到期后系统自动降级到其他数据源
    """

    name = "tickdb"

    def is_available(self) -> bool:
        return bool(TICKDB_KEY)

    # ── 1. 支持的股票列表 ────────────────────────────────────
    def get_tickers(self) -> Optional[list]:
        """
        GET /v1/tickers
        Header: Authorization: Bearer TOKEN
        响应: {tickers: [{symbol, name, exchange, type}]}
        """
        data = _get("/v1/tickers")
        if not data:
            return None
        return data.get("tickers", data) if isinstance(data, dict) else data

    # ── 2. 实时报价 ──────────────────────────────────────────
    def get_quote(self, symbol: str) -> Optional[dict]:
        """
        GET /v1/quote/{symbol}
        Header: Authorization: Bearer TOKEN
        响应: {symbol, price, change, changePct, volume, high, low, open, prevClose, timestamp}
        """
        data = _get(f"/v1/quote/{symbol.upper()}")
        if not data:
            return None
        # 适配不同的响应格式
        if isinstance(data, list) and data:
            data = data[0]
        return {
            "ticker":     symbol.upper(),
            "price":      round(float(data.get("price", 0)), 2),
            "change":     round(float(data.get("change", 0)), 2),
            "change_pct": round(float(data.get("changePct", data.get("change_pct", 0))), 2),
            "volume":     int(data.get("volume", 0)),
            "high":       data.get("high"),
            "low":        data.get("low"),
            "open":       data.get("open"),
            "prev_close": data.get("prevClose", data.get("prev_close")),
            "timestamp":  data.get("timestamp"),
            "source":     "tickdb",
        }

    # ── 3. 历史OHLCV ─────────────────────────────────────────
    def get_ohlcv(self, symbol: str, timeframe: str = "3mo") -> Optional[dict]:
        """
        GET /v1/ohlcv/{symbol}?from=YYYY-MM-DD&to=YYYY-MM-DD&resolution=1d
        参数:
          from:       开始日期 YYYY-MM-DD
          to:         结束日期 YYYY-MM-DD
          resolution: 1m/5m/15m/30m/1h/1d/1w  (分钟/小时/日/周)
        响应: {candles: [{time,open,high,low,close,volume}]}
        """
        from datetime import datetime, timedelta
        period_map = {
            "1d":  (1,    "5m"),
            "5d":  (5,    "15m"),
            "1mo": (30,   "1h"),
            "3mo": (90,   "1d"),
            "6mo": (180,  "1d"),
            "1y":  (365,  "1d"),
            "5y":  (1825, "1w"),
        }
        days, resolution = period_map.get(timeframe, (90, "1d"))
        today = datetime.utcnow()
        frm = (today - timedelta(days=days)).strftime("%Y-%m-%d")
        to  = today.strftime("%Y-%m-%d")

        data = _get(f"/v1/ohlcv/{symbol.upper()}", {
            "from":       frm,
            "to":         to,
            "resolution": resolution,
        })
        if not data:
            return None

        raw_candles = data.get("candles", data.get("data", []))
        if not raw_candles:
            return None

        candles = []
        for c in raw_candles:
            t = c.get("time", c.get("timestamp", 0))
            if isinstance(t, str):
                try:
                    t = int(datetime.fromisoformat(t.replace("Z","")).timestamp() * 1000)
                except Exception:
                    t = 0
            candles.append({
                "time":   t,
                "open":   round(float(c.get("open", 0)), 2),
                "high":   round(float(c.get("high", 0)), 2),
                "low":    round(float(c.get("low", 0)), 2),
                "close":  round(float(c.get("close", 0)), 2),
                "volume": int(c.get("volume", 0)),
            })
        return {"ticker": symbol.upper(), "timeframe": timeframe, "candles": candles} if candles else None

