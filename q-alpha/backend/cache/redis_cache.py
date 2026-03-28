"""
Q-Alpha Cache Manager
Redis-based caching with automatic in-memory fallback.
"""

import json
import time
import logging
from typing import Any, Optional

logger = logging.getLogger("q-alpha.cache")

# In-memory fallback cache
_memory_cache: dict = {}


def _get_redis():
    """Get Redis client or None if unavailable."""
    try:
        import redis
        from config.settings import settings
        if not settings.REDIS_ENABLED:
            return None
        r = redis.from_url(settings.REDIS_URL, decode_responses=True, socket_timeout=2)
        r.ping()
        return r
    except Exception:
        return None


def cache_get(key: str) -> Optional[Any]:
    """Get value from cache."""
    r = _get_redis()
    if r:
        try:
            val = r.get(f"qalpha:{key}")
            if val:
                return json.loads(val)
        except Exception as e:
            logger.warning(f"Redis get error: {e}")

    # Fallback to memory cache
    entry = _memory_cache.get(key)
    if entry and entry["expires"] > time.time():
        return entry["value"]
    return None


def cache_set(key: str, value: Any, ttl: int = 60):
    """Set value in cache with TTL (seconds)."""
    r = _get_redis()
    if r:
        try:
            r.setex(f"qalpha:{key}", ttl, json.dumps(value, default=str))
            return
        except Exception as e:
            logger.warning(f"Redis set error: {e}")

    # Fallback to memory cache
    _memory_cache[key] = {
        "value": value,
        "expires": time.time() + ttl,
    }


def cache_delete(key: str):
    """Delete a cache key."""
    r = _get_redis()
    if r:
        try:
            r.delete(f"qalpha:{key}")
        except Exception:
            pass
    _memory_cache.pop(key, None)


def cache_flush_pattern(pattern: str):
    """Flush all keys matching a pattern."""
    r = _get_redis()
    if r:
        try:
            keys = r.keys(f"qalpha:{pattern}*")
            if keys:
                r.delete(*keys)
        except Exception as e:
            logger.warning(f"Redis flush error: {e}")
