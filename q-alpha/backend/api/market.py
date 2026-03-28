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


def _cached_payload(cached):
    if isinstance(cached, dict) and "data" in cached:
        return cached.get("data"), cached.get("meta", {})
    if isinstance(cached, dict):
        src = cached.get("source", "unknown")
    elif isinstance(cached, list) and cached and isinstance(cached[0], dict):
        src = cached[0].get("source", "unknown")
    else:
        src = "unknown"
    return cached, {"selected_source": src, "source_plan": ["cache_legacy"]}


@router.get("/popular")
@limiter.limit("30/minute")
async def get_popular(request: Request, ticker: str = Query(None)):
    """Get popular/trending stocks with prices."""
    cache_key = f"market:popular:{ticker or 'all'}"
    cached = cache_get(cache_key)
    if cached:
        data, meta = _cached_payload(cached)
        return {"data": data, "meta": meta, "cached": True}

    provider = get_provider()
    params = {"ticker": ticker} if ticker else {}
    payload = provider.fetch_with_meta("market/popular", params, source_type="stock")
    data = payload.get("data")
    if ticker and isinstance(data, list):
        data = [d for d in data if d.get("ticker") == ticker.upper()]

    payload["data"] = data
    cache_set(cache_key, payload, ttl=settings.CACHE_TTL_STOCK)
    return {"data": data, "meta": payload.get("meta"), "cached": False}


@router.get("/news")
@limiter.limit("20/minute")
async def get_news(request: Request):
    """Get trending financial news feed."""
    cache_key = "market:news"
    cached = cache_get(cache_key)
    if cached:
        data, meta = _cached_payload(cached)
        return {"data": data, "meta": meta, "cached": True}

    provider = get_provider()
    payload = provider.fetch_with_meta("market/news", {})
    cache_set(cache_key, payload, ttl=300)
    return {"data": payload.get("data"), "meta": payload.get("meta"), "cached": False}
