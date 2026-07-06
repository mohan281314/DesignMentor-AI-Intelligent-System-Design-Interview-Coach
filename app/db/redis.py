"""
Redis client configuration and utilities.
"""

from __future__ import annotations

import json
from typing import Any

import redis.asyncio as aioredis
from redis.asyncio import Redis

from app.core.config import get_settings

settings = get_settings()


class RedisClient:
    """Async Redis client wrapper with convenience methods."""
    
    def __init__(self):
        self._client: Redis | None = None
    
    async def connect(self):
        """Establish Redis connection."""
        if self._client is None:
            self._client = await aioredis.from_url(
                settings.redis_url,
                encoding="utf-8",
                decode_responses=True,
            )
    
    async def close(self):
        """Close Redis connection."""
        if self._client:
            await self._client.close()
            self._client = None
    
    @property
    def client(self) -> Redis:
        """Get Redis client instance."""
        if self._client is None:
            raise RuntimeError("Redis client not connected. Call connect() first.")
        return self._client
    
    async def get(self, key: str) -> str | None:
        """Get value by key."""
        return await self.client.get(key)
    
    async def set(
        self, 
        key: str, 
        value: str | dict | list, 
        ex: int | None = None
    ) -> bool:
        """
        Set key-value pair with optional expiration.
        
        Args:
            key: Redis key
            value: Value to store (auto-serialized if dict/list)
            ex: Expiration time in seconds
        """
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        return await self.client.set(key, value, ex=ex)
    
    async def get_json(self, key: str) -> dict | list | None:
        """Get JSON value by key."""
        value = await self.get(key)
        if value:
            return json.loads(value)
        return None
    
    async def delete(self, *keys: str) -> int:
        """Delete one or more keys."""
        return await self.client.delete(*keys)
    
    async def exists(self, *keys: str) -> int:
        """Check if keys exist."""
        return await self.client.exists(*keys)
    
    async def expire(self, key: str, seconds: int) -> bool:
        """Set expiration on key."""
        return await self.client.expire(key, seconds)
    
    async def incr(self, key: str) -> int:
        """Increment integer value."""
        return await self.client.incr(key)
    
    async def decr(self, key: str) -> int:
        """Decrement integer value."""
        return await self.client.decr(key)
    
    # Cache decorator helper
    async def cache_get_or_set(
        self,
        key: str,
        factory_fn,
        ex: int = 3600,
    ) -> Any:
        """
        Get from cache or compute and cache the result.
        
        Args:
            key: Cache key
            factory_fn: Async function to compute value if cache miss
            ex: Cache expiration in seconds (default: 1 hour)
        """
        cached = await self.get_json(key)
        if cached is not None:
            return cached
        
        # Cache miss - compute value
        result = await factory_fn()
        await self.set(key, result, ex=ex)
        return result


# Global Redis instance
redis_client = RedisClient()


async def get_redis() -> RedisClient:
    """Dependency function for FastAPI to get Redis client."""
    return redis_client
