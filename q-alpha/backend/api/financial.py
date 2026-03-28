"""
Q-Alpha Financial & Corporate API
Endpoints: /api/insider, /api/whales, /api/etf, /api/analyst, etc.
"""

import logging
from fastapi import APIRouter, Query, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from cache.redis_cache import cache_get, cache_set
from data_sources.provider import get_provider
from config.settings import settings

logger = logging.getLogger("q-alpha.api.financial")
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


def _cached_route(cache_key: str, fetch_fn, ttl: int):
    cached = cache_get(cache_key)
    if cached:
        data, meta = _cached_payload(cached)
        return {"data": data, "meta": meta, "cached": True}
    payload = fetch_fn()
    cache_set(cache_key, payload, ttl=ttl)
    return {"data": payload.get("data"), "meta": payload.get("meta"), "cached": False}


@router.get("/insider")
@limiter.limit("30/minute")
async def insider_trading(request: Request, ticker: str = Query(...)):
    return _cached_route(
        f"insider:{ticker.upper()}",
        lambda: get_provider().fetch_with_meta("insider", {"ticker": ticker.upper()}, source_type="sec"),
        settings.CACHE_TTL_INSIDER,
    )


@router.get("/whales")
@limiter.limit("30/minute")
async def whale_moves(request: Request, ticker: str = Query(...)):
    return _cached_route(
        f"whales:{ticker.upper()}",
        lambda: get_provider().fetch_with_meta("whales", {"ticker": ticker.upper()}),
        settings.CACHE_TTL_WHALE,
    )


@router.get("/institutional")
@limiter.limit("30/minute")
async def institutional(request: Request, ticker: str = Query(...)):
    return _cached_route(
        f"institutional:{ticker.upper()}",
        lambda: get_provider().fetch_with_meta("institutional", {"ticker": ticker.upper()}),
        settings.CACHE_TTL_WHALE,
    )


@router.get("/analyst")
@limiter.limit("30/minute")
async def analyst_ratings(request: Request, ticker: str = Query(...)):
    return _cached_route(
        f"analyst:{ticker.upper()}",
        lambda: get_provider().fetch_with_meta("analyst", {"ticker": ticker.upper()}),
        settings.CACHE_TTL_POLITICIANS,
    )


@router.get("/sec")
@limiter.limit("20/minute")
async def sec_filings(request: Request, ticker: str = Query(...)):
    return _cached_route(
        f"sec:{ticker.upper()}",
        lambda: get_provider().fetch_with_meta("sec", {"ticker": ticker.upper()}, source_type="sec"),
        settings.CACHE_TTL_POLITICIANS,
    )


@router.get("/revenue")
@limiter.limit("20/minute")
async def revenue_breakdown(request: Request, ticker: str = Query(...)):
    return _cached_route(
        f"revenue:{ticker.upper()}",
        lambda: get_provider().fetch_with_meta("revenue", {"ticker": ticker.upper()}),
        settings.CACHE_TTL_DAILY,
    )


@router.get("/risk")
@limiter.limit("20/minute")
async def risk_factors(request: Request, ticker: str = Query(...)):
    return _cached_route(
        f"risk:{ticker.upper()}",
        lambda: get_provider().fetch_with_meta("risk", {"ticker": ticker.upper()}),
        settings.CACHE_TTL_DAILY,
    )


@router.get("/etf")
@limiter.limit("20/minute")
async def etf_holdings(request: Request, ticker: str = Query(...)):
    return _cached_route(
        f"etf:{ticker.upper()}",
        lambda: get_provider().fetch_with_meta("etf", {"ticker": ticker.upper()}, source_type="stock"),
        settings.CACHE_TTL_WHALE,
    )


@router.get("/splits")
@limiter.limit("20/minute")
async def stock_splits(request: Request, ticker: str = Query(...)):
    return _cached_route(
        f"splits:{ticker.upper()}",
        lambda: get_provider().fetch_with_meta("splits", {"ticker": ticker.upper()}, source_type="stock"),
        settings.CACHE_TTL_WHALE,
    )


@router.get("/trends")
@limiter.limit("20/minute")
async def google_trends(request: Request, keyword: str = Query(...)):
    return _cached_route(
        f"trends:{keyword.lower()}",
        lambda: get_provider().fetch_with_meta("trends", {"keyword": keyword}),
        settings.CACHE_TTL_TRENDS,
    )


@router.get("/consumer")
@limiter.limit("20/minute")
async def consumer_interest(request: Request, keyword: str = Query(...)):
    return _cached_route(
        f"consumer:{keyword.lower()}",
        lambda: get_provider().fetch_with_meta("consumer", {"keyword": keyword}),
        settings.CACHE_TTL_TRENDS,
    )


@router.get("/patents")
@limiter.limit("20/minute")
async def patents(request: Request, company_name: str = Query(...)):
    return _cached_route(
        f"patents:{company_name.lower()}",
        lambda: get_provider().fetch_with_meta("patents", {"company_name": company_name}),
        settings.CACHE_TTL_DAILY,
    )


@router.get("/media/cnbc")
@limiter.limit("20/minute")
async def cnbc_picks(request: Request, ticker: str = Query(None)):
    return _cached_route(
        f"media:cnbc:{ticker or 'all'}",
        lambda: get_provider().fetch_with_meta("media/cnbc", {"ticker": ticker or ""}),
        settings.CACHE_TTL_DAILY,
    )


@router.get("/media/cramer")
@limiter.limit("20/minute")
async def cramer_tracker(request: Request, ticker: str = Query(None)):
    return _cached_route(
        f"media:cramer:{ticker or 'all'}",
        lambda: get_provider().fetch_with_meta("media/cramer", {"ticker": ticker or ""}),
        settings.CACHE_TTL_DAILY,
    )


@router.get("/app-ratings")
@limiter.limit("20/minute")
async def app_ratings(request: Request, app_name: str = Query(...)):
    return _cached_route(
        f"app-ratings:{app_name.lower()}",
        lambda: get_provider().fetch_with_meta("app-ratings", {"app_name": app_name}),
        settings.CACHE_TTL_DAILY,
    )
