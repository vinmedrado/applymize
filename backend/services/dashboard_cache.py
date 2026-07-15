from __future__ import annotations

import time
from typing import Any

_CACHE: dict[str, tuple[dict[str, Any], float]] = {}
TTL_SECONDS = 30


def get_cache(key: str) -> dict[str, Any] | None:
    item = _CACHE.get(key)
    if not item:
        return None
    value, ts = item
    if time.time() - ts > TTL_SECONDS:
        _CACHE.pop(key, None)
        return None
    return value


def set_cache(key: str, value: dict[str, Any]) -> dict[str, Any]:
    _CACHE[key] = (value, time.time())
    return value


def invalidate_cache(prefix: str | None = None) -> None:
    if not prefix:
        _CACHE.clear()
        return
    for key in list(_CACHE.keys()):
        if key.startswith(prefix):
            _CACHE.pop(key, None)
