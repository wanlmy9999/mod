"""
聚合数据 (Juhe) 美股数据提供商
API Key: ac627c20cf0cb1a7a80622b10eaf604d
接口地址: http://web.juhe.cn/finance/stock/usa
文档: https://www.juhe.cn/docs/api/id/21
调用方式: GET http://web.juhe.cn/finance/stock/usa?key=KEY&gid=aapl
注意: gid 使用小写股票代码，返回实时行情
"""

import logging
import requests
from typing import Any, Optional

logger = logging.getLogger("q-alpha.juhe")

JUHE_BASE = "http://web.juhe.cn/finance/stock/usa"
JUHE_KEY  = "ac627c20cf0cb1a7a80622b10eaf604d"


def _get(params: dict) -> Optional[dict]:
    """发起聚合数据 GET 请求"""
    try:
        params["key"] = JUHE_KEY
        resp = requests.get(JUHE_BASE, params=params, timeout=8)
        resp.raise_for_status()
        data = resp.json()
        if data.get("error_code") != 0:
            logger.warning(f"聚合API错误: {data.get('reason')} (code={data.get('error_code')})")
            return None
        return data
    except requests.exceptions.RequestException as e:
        logger.warning(f"聚合API请求失败: {e}")
        return None


class JuheProvider:
    """
    聚合数据美股实时报价提供商
    接口: GET http://web.juhe.cn/finance/stock/usa?key=KEY&gid=aapl
    响应结构:
      {
        "reason": "success",
        "result": [{
          "name":         "苹果",
          "engName":      "Apple Inc.",
          "preClosePrice":"188.27",
          "openPrice":    "188.20",
          "nowPrice":     "189.50",  ← 当前价格
          "highPrice":    "190.10",
          "lowPrice":     "187.80",
          "volume":       "52345678",
          "amount":       "9876543210",
          "updown":       "1.23",    ← 涨跌额
          "percent":      "0.65%",   ← 涨跌幅
          "time":         "16:00:00",
          "date":         "2024-01-15",
          "marketValue":  "2950000000000"
        }],
        "error_code": 0
      }
    """

    name = "juhe"

    def is_available(self) -> bool:
        return bool(JUHE_KEY)

    def get_quote(self, symbol: str) -> Optional[dict]:
        """
        获取美股实时报价
        参数: gid=股票代码(小写，如 aapl/tsla/nvda)
        """
        data = _get({"gid": symbol.lower()})
        if not data or not data.get("result"):
            return None
        r = data["result"][0]

        # 解析涨跌幅 (去掉%号)
        percent_str = str(r.get("percent", "0%")).replace("%", "").replace("+", "")
        try:
            change_pct = float(percent_str)
        except ValueError:
            change_pct = 0.0

        try:
            change = float(r.get("updown", 0))
        except ValueError:
            change = 0.0

        try:
            price = float(r.get("nowPrice", 0))
        except ValueError:
            price = 0.0

        return {
            "ticker":     symbol.upper(),
            "name":       r.get("name", symbol),
            "name_en":    r.get("engName", symbol),
            "price":      price,
            "change":     change,
            "change_pct": change_pct,
            "open":       float(r.get("openPrice", 0) or 0),
            "high":       float(r.get("highPrice", 0) or 0),
            "low":        float(r.get("lowPrice", 0) or 0),
            "prev_close": float(r.get("preClosePrice", 0) or 0),
            "volume":     int(r.get("volume", 0) or 0),
            "amount":     float(r.get("amount", 0) or 0),
            "trade_time": r.get("time", ""),
            "trade_date": r.get("date", ""),
            "source":     "juhe",
        }

    def get_batch_quotes(self, symbols: list) -> list:
        """
        批量获取报价（逐一调用，聚合API不支持批量）
        最多20个，每个间隔0.2秒防止超频
        """
        import time
        results = []
        for sym in symbols[:20]:
            q = self.get_quote(sym)
            if q:
                results.append(q)
            time.sleep(0.2)
        return results

