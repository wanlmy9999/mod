"""
Q-Alpha AI Analysis API
Endpoints: /api/stock/price, /api/stock/candles, /api/ai/analyze, /api/portfolio/famous
"""

import logging
from fastapi import APIRouter, Query, Request
from pydantic import BaseModel
from typing import Optional, List
from slowapi import Limiter
from slowapi.util import get_remote_address
from cache.redis_cache import cache_get, cache_set
from data_sources.provider import get_provider
from ai_engine.analyzer import get_analyzer
from config.settings import settings

logger = logging.getLogger("q-alpha.api.ai")
router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


class AnalyzeRequest(BaseModel):
    ticker: str
    options: Optional[dict] = {}


@router.get("/stock/price")
@limiter.limit("60/minute")
async def stock_price(request: Request, ticker: str = Query(...)):
    """Get current stock price with change data."""
    t = ticker.upper()
    cache_key = f"stock:price:{t}"
    cached = cache_get(cache_key)
    if cached:
        return {"data": cached, "cached": True}

    provider = get_provider()
    data = provider.fetch("stock/price", {"ticker": t}, source_type="stock")
    if data:
        cache_set(cache_key, data, ttl=settings.CACHE_TTL_STOCK)
    return {"data": data, "cached": False}


@router.get("/stock/info")
@limiter.limit("30/minute")
async def stock_info(request: Request, ticker: str = Query(...)):
    """Get detailed stock information."""
    t = ticker.upper()
    cache_key = f"stock:info:{t}"
    cached = cache_get(cache_key)
    if cached:
        return {"data": cached, "cached": True}

    provider = get_provider()
    data = provider.fetch("stock/info", {"ticker": t}, source_type="stock")
    if data:
        cache_set(cache_key, data, ttl=3600)
    return {"data": data, "cached": False}


@router.get("/stock/candles")
@limiter.limit("30/minute")
async def stock_candles(
    request: Request,
    ticker: str = Query(...),
    timeframe: str = Query("3mo", description="1d|5d|1mo|3mo|6mo|1y|5y"),
):
    """Get OHLCV candlestick data."""
    t = ticker.upper()
    cache_key = f"stock:candles:{t}:{timeframe}"
    cached = cache_get(cache_key)
    if cached:
        return {"data": cached, "cached": True}

    provider = get_provider()
    data = provider.fetch("stock/candles", {"ticker": t, "timeframe": timeframe}, source_type="stock")
    if data:
        ttl = settings.CACHE_TTL_STOCK if timeframe in ("1d", "5d") else 300
        cache_set(cache_key, data, ttl=ttl)
    return {"data": data, "cached": False}


@router.post("/ai/analyze")
@limiter.limit("10/minute")
async def ai_analyze(request: Request, body: AnalyzeRequest):
    """
    Run full AI analysis on a ticker.
    Returns score (0-100), rating (BUY/HOLD/SELL), explanation, risk flags.
    """
    t = body.ticker.upper()
    cache_key = f"ai:analyze:{t}"
    cached = cache_get(cache_key)
    if cached:
        return {"data": cached, "cached": True}

    provider = get_provider()

    # Gather all input signals in parallel (best effort)
    candle_data = provider.fetch("stock/candles", {"ticker": t, "timeframe": "3mo"}, source_type="stock")
    insider_data = provider.fetch("insider", {"ticker": t}, source_type="sec")
    whale_data = provider.fetch("whales", {"ticker": t})
    analyst_data = provider.fetch("analyst", {"ticker": t})

    analyzer = get_analyzer()
    result = analyzer.analyze(
        ticker=t,
        candle_data=candle_data,
        insider_data=insider_data if isinstance(insider_data, list) else [],
        whale_data=whale_data if isinstance(whale_data, list) else [],
        analyst_data=analyst_data if isinstance(analyst_data, list) else [],
    )

    cache_set(cache_key, result, ttl=settings.CACHE_TTL_AI)
    return {"data": result, "cached": False}


@router.get("/ai/analyze")
@limiter.limit("10/minute")
async def ai_analyze_get(request: Request, ticker: str = Query(...)):
    """GET version of AI analysis for convenience."""
    t = ticker.upper()
    cache_key = f"ai:analyze:{t}"
    cached = cache_get(cache_key)
    if cached:
        return {"data": cached, "cached": True}

    provider = get_provider()
    candle_data = provider.fetch("stock/candles", {"ticker": t, "timeframe": "3mo"}, source_type="stock")
    insider_data = provider.fetch("insider", {"ticker": t}, source_type="sec")
    whale_data = provider.fetch("whales", {"ticker": t})
    analyst_data = provider.fetch("analyst", {"ticker": t})

    analyzer = get_analyzer()
    result = analyzer.analyze(
        ticker=t,
        candle_data=candle_data,
        insider_data=insider_data if isinstance(insider_data, list) else [],
        whale_data=whale_data if isinstance(whale_data, list) else [],
        analyst_data=analyst_data if isinstance(analyst_data, list) else [],
    )
    cache_set(cache_key, result, ttl=settings.CACHE_TTL_AI)
    return {"data": result, "cached": False}


@router.get("/portfolio/famous")
@limiter.limit("20/minute")
async def famous_portfolio(request: Request, celebrity_name: str = Query(...)):
    """Get famous investor/politician portfolio holdings."""
    cache_key = f"portfolio:famous:{celebrity_name.lower()}"
    cached = cache_get(cache_key)
    if cached:
        return {"data": cached, "cached": True}

    provider = get_provider()
    data = provider.fetch("portfolio/famous", {"celebrity_name": celebrity_name})
    cache_set(cache_key, data, ttl=settings.CACHE_TTL_POLITICIANS)
    return {"data": data, "cached": False}
