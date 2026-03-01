"""Simple TTL cache for expensive API calls."""
import time
from typing import Any

_cache: dict[str, tuple[float, Any]] = {}

def get_cached(key: str, ttl: int = 300) -> Any | None:
    """Get cached value if not expired. Default TTL 5 min."""
    if key in _cache:
        ts, val = _cache[key]
        if time.time() - ts < ttl:
            return val
    return None

def set_cached(key: str, value: Any, ttl: int = 300):
    """Store value in cache. ttl param accepted for clarity but TTL is checked on read."""
    _cache[key] = (time.time(), value)
