from __future__ import annotations

import json
import time
from dataclasses import dataclass
from typing import Any

import redis


@dataclass
class CacheItem:
    value: dict[str, Any]
    expires_at: float


class RecommendationCache:
    def __init__(self, redis_url: str, ttl_seconds: int = 3600) -> None:
        self.ttl_seconds = ttl_seconds
        self.memory_store: dict[str, CacheItem] = {}
        self.redis_client = None
        try:
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
            self.redis_client.ping()
        except Exception:
            self.redis_client = None

    def get(self, key: str) -> dict[str, Any] | None:
        if self.redis_client is not None:
            raw = self.redis_client.get(key)
            return json.loads(raw) if raw else None
        item = self.memory_store.get(key)
        if not item:
            return None
        if item.expires_at < time.time():
            self.memory_store.pop(key, None)
            return None
        return item.value

    def set(self, key: str, value: dict[str, Any]) -> None:
        serialized = json.dumps(value, default=str)
        if self.redis_client is not None:
            self.redis_client.setex(key, self.ttl_seconds, serialized)
            return
        self.memory_store[key] = CacheItem(value=value, expires_at=time.time() + self.ttl_seconds)
