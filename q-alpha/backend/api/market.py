"""
Q-Alpha Market API
Endpoints: /api/market/popular, /api/market/news
"""

import logging
from fastapi import APIRouter, Query, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from cache.redis_cache import cache_get, cache_set
from data_sources.provider import get_provider
from config.settings import settings

logger = logging.getLogger("q-alpha.api.market")
router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


@router.get("/popular")
@limiter.limit("30/minute")
async def get_popular(request: Request, ticker: str = Query(None)):
    """Get popular/trending stocks with prices."""
    cache_key = f"market:popular:{ticker or 'all'}"
    cached = cache_get(cache_key)
    if cached:
        return {"data": cached, "cached": True}

    provider = get_provider()
    params = {"ticker": ticker} if ticker else {}
    data = provider.fetch("market/popular", params, source_type="stock")
    if ticker and isinstance(data, list):
        data = [d for d in data if d.get("ticker") == ticker.upper()]

    cache_set(cache_key, data, ttl=settings.CACHE_TTL_STOCK)
    return {"data": data, "cached": False}


@router.get("/news")
@limiter.limit("20/minute")
async def get_news(request: Request):
    """Get trending financial news feed."""
    cache_key = "market:news"
    cached = cache_get(cache_key)
    if cached:
        return {"data": cached, "cached": True}

    provider = get_provider()
    data = provider.fetch("market/news", {})
    cache_set(cache_key, data, ttl=300)
    return {"data": data, "cached": False}
