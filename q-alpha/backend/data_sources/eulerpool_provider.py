"""
EulerPool 数据提供商
说明：优先尝试 EulerPool API，失败时返回 None 交由上层 fallback。
"""

from __future__ import annotations

import logging
import os
from typing import Optional

import requests

logger = logging.getLogger("q-alpha.eulerpool")

EULERPOOL_BASE = os.getenv("EULERPOOL_BASE_URL", "https://api.eulerpool.com")
EULERPOOL_KEY = os.getenv("EULERPOOL_API_KEY", "eu_prod_1774678674268_kcnp2gtuvbt")


class EulerPoolProvider:
    name = "eulerpool"

    def is_available(self) -> bool:
        return bool(EULERPOOL_KEY)

    def _get(self, path: str, params: dict) -> Optional[dict]:
        if not EULERPOOL_KEY:
            return None
        try:
            resp = requests.get(
                f"{EULERPOOL_BASE}{path}",
                headers={"Authorization": f"Bearer {EULERPOOL_KEY}"},
                params=params,
                timeout=8,
            )
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            logger.warning(f"EulerPool request failed {path}: {e}")
            return None

    def get_quote(self, symbol: str) -> Optional[dict]:
        data = self._get("/v1/market/quote", {"symbol": symbol.upper()})
        if not data:
            return None
        return {
            "ticker": symbol.upper(),
            "price": float(data.get("price", 0) or 0),
            "change": float(data.get("change", 0) or 0),
            "change_pct": float(data.get("change_pct", 0) or 0),
            "high": data.get("high"),
            "low": data.get("low"),
            "open": data.get("open"),
            "prev_close": data.get("prev_close"),
            "volume": data.get("volume", 0),
            "source": "eulerpool",
        }

    def get_candles(self, symbol: str, timeframe: str = "3mo") -> Optional[dict]:
        data = self._get("/v1/market/candles", {"symbol": symbol.upper(), "timeframe": timeframe})
        if not data:
            return None
        candles = data.get("candles", [])
        if not candles:
            return None
        return {"ticker": symbol.upper(), "timeframe": timeframe, "candles": candles}

    def get_profile(self, symbol: str) -> Optional[dict]:
        data = self._get("/v1/market/profile", {"symbol": symbol.upper()})
        return data if data else None
