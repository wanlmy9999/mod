"""
Q-Alpha Politicians & Government API
Endpoints: /api/politician/search, /api/gov/*
"""

import logging
from fastapi import APIRouter, Query, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from cache.redis_cache import cache_get, cache_set
from data_sources.provider import get_provider
from config.settings import settings

logger = logging.getLogger("q-alpha.api.politicians")
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


@router.get("/politician/search")
@limiter.limit("30/minute")
async def politician_search(request: Request, name: str = Query(..., description="Politician name to search")):
    cache_key = f"politician:search:{name.lower()}"
    cached = cache_get(cache_key)
    if cached:
        data, meta = _cached_payload(cached)
        return {"data": data, "meta": meta, "cached": True}

    provider = get_provider()
    payload = provider.fetch_with_meta("politician/search", {"name": name})
    cache_set(cache_key, payload, ttl=settings.CACHE_TTL_POLITICIANS)
    return {"data": payload.get("data"), "meta": payload.get("meta"), "cached": False}


@router.get("/gov/congress-trading")
@limiter.limit("30/minute")
async def congress_trading(request: Request, member_name: str = Query(None)):
    cache_key = f"gov:congress-trading:{(member_name or 'all').lower()}"
    cached = cache_get(cache_key)
    if cached:
        data, meta = _cached_payload(cached)
        return {"data": data, "meta": meta, "cached": True}

    provider = get_provider()
    payload = provider.fetch_with_meta("gov/congress-trading", {"member_name": member_name or ""})
    cache_set(cache_key, payload, ttl=settings.CACHE_TTL_POLITICIANS)
    return {"data": payload.get("data"), "meta": payload.get("meta"), "cached": False}


@router.get("/gov/elections")
@limiter.limit("20/minute")
async def elections(request: Request, year: int = Query(2026)):
    cache_key = f"gov:elections:{year}"
    cached = cache_get(cache_key)
    if cached:
        data, meta = _cached_payload(cached)
        return {"data": data, "meta": meta, "cached": True}

    provider = get_provider()
    payload = provider.fetch_with_meta("gov/elections", {"year": year})
    cache_set(cache_key, payload, ttl=settings.CACHE_TTL_DAILY)
    return {"data": payload.get("data"), "meta": payload.get("meta"), "cached": False}


@router.get("/gov/fundraising")
@limiter.limit("20/minute")
async def fundraising(request: Request, politician_name: str = Query(...)):
    cache_key = f"gov:fundraising:{politician_name.lower()}"
    cached = cache_get(cache_key)
    if cached:
        data, meta = _cached_payload(cached)
        return {"data": data, "meta": meta, "cached": True}

    provider = get_provider()
    payload = provider.fetch_with_meta("gov/fundraising", {"politician_name": politician_name})
    cache_set(cache_key, payload, ttl=settings.CACHE_TTL_DAILY)
    return {"data": payload.get("data"), "meta": payload.get("meta"), "cached": False}


@router.get("/gov/contracts")
@limiter.limit("20/minute")
async def contracts(request: Request, agency_name: str = Query(None)):
    cache_key = f"gov:contracts:{(agency_name or 'all').lower()}"
    cached = cache_get(cache_key)
    if cached:
        data, meta = _cached_payload(cached)
        return {"data": data, "meta": meta, "cached": True}

    provider = get_provider()
    payload = provider.fetch_with_meta("gov/contracts", {"agency_name": agency_name or ""})
    cache_set(cache_key, payload, ttl=settings.CACHE_TTL_DAILY)
    return {"data": payload.get("data"), "meta": payload.get("meta"), "cached": False}


@router.get("/gov/lobbying")
@limiter.limit("20/minute")
async def lobbying(request: Request, company_name: str = Query(...)):
    cache_key = f"gov:lobbying:{company_name.lower()}"
    cached = cache_get(cache_key)
    if cached:
        data, meta = _cached_payload(cached)
        return {"data": data, "meta": meta, "cached": True}

    provider = get_provider()
    payload = provider.fetch_with_meta("gov/lobbying", {"company_name": company_name})
    cache_set(cache_key, payload, ttl=settings.CACHE_TTL_POLITICIANS)
    return {"data": payload.get("data"), "meta": payload.get("meta"), "cached": False}


@router.get("/gov/spending")
@limiter.limit("20/minute")
async def spending(request: Request, agency_name: str = Query(None)):
    cache_key = f"gov:spending:{(agency_name or 'all').lower()}"
    cached = cache_get(cache_key)
    if cached:
        data, meta = _cached_payload(cached)
        return {"data": data, "meta": meta, "cached": True}

    provider = get_provider()
    payload = provider.fetch_with_meta("gov/spending", {"agency_name": agency_name or ""})
    cache_set(cache_key, payload, ttl=settings.CACHE_TTL_DAILY)
    return {"data": payload.get("data"), "meta": payload.get("meta"), "cached": False}


@router.get("/gov/networth")
@limiter.limit("20/minute")
async def networth(request: Request, member_name: str = Query(...)):
    cache_key = f"gov:networth:{member_name.lower()}"
    cached = cache_get(cache_key)
    if cached:
        data, meta = _cached_payload(cached)
        return {"data": data, "meta": meta, "cached": True}

    provider = get_provider()
    payload = provider.fetch_with_meta("gov/networth", {"member_name": member_name})
    cache_set(cache_key, payload, ttl=settings.CACHE_TTL_POLITICIANS)
    return {"data": payload.get("data"), "meta": payload.get("meta"), "cached": False}


@router.get("/gov/insider-score")
@limiter.limit("20/minute")
async def insider_score(request: Request, member_name: str = Query(...)):
    cache_key = f"gov:insider-score:{member_name.lower()}"
    cached = cache_get(cache_key)
    if cached:
        data, meta = _cached_payload(cached)
        return {"data": data, "meta": meta, "cached": True}

    provider = get_provider()
    payload = provider.fetch_with_meta("gov/insider-score", {"member_name": member_name})
    cache_set(cache_key, payload, ttl=settings.CACHE_TTL_POLITICIANS)
    return {"data": payload.get("data"), "meta": payload.get("meta"), "cached": False}


@router.get("/gov/corporate-donations")
@limiter.limit("20/minute")
async def corporate_donations(request: Request, company_name: str = Query(...)):
    cache_key = f"gov:corp-donations:{company_name.lower()}"
    cached = cache_get(cache_key)
    if cached:
        data, meta = _cached_payload(cached)
        return {"data": data, "meta": meta, "cached": True}

    provider = get_provider()
    payload = provider.fetch_with_meta("gov/corporate-donations", {"company_name": company_name})
    cache_set(cache_key, payload, ttl=settings.CACHE_TTL_POLITICIANS)
    return {"data": payload.get("data"), "meta": payload.get("meta"), "cached": False}
