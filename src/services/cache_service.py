"""Redis cache service for optimizing API calls."""

import json
import hashlib
from typing import Any, Optional
import redis.asyncio as aioredis

from src.config.settings import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)


class CacheService:
    """Redis-based caching service."""

    def __init__(self):
        """Initialize cache service."""
        self.client: Optional[aioredis.Redis] = None
        self.enabled = settings.cache_enabled
        self.default_ttl = settings.cache_ttl_seconds

    async def connect(self) -> None:
        """Establish connection to Redis."""
        if not self.enabled:
            logger.info("Cache is disabled")
            return

        try:
            self.client = await aioredis.from_url(
                f"{'rediss' if settings.redis_ssl else 'redis'}://{settings.redis_host}:{settings.redis_port}",
                password=settings.redis_password,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=5,
                socket_keepalive=True,
            )
            await self.client.ping()
            logger.info("Successfully connected to Redis cache")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.enabled = False

    async def disconnect(self) -> None:
        """Close Redis connection."""
        if self.client:
            await self.client.close()
            logger.info("Disconnected from Redis cache")

    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """
        Generate a cache key from arguments.

        Args:
            prefix: Key prefix (e.g., 'ariba:po')
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Generated cache key
        """
        key_data = f"{prefix}:{args}:{sorted(kwargs.items())}"
        key_hash = hashlib.md5(key_data.encode()).hexdigest()
        return f"{prefix}:{key_hash}"

    async def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None
        """
        if not self.enabled or not self.client:
            return None

        try:
            value = await self.client.get(key)
            if value:
                logger.debug(f"Cache hit: {key}")
                return json.loads(value)
            logger.debug(f"Cache miss: {key}")
            return None
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None

    async def set(
        self, key: str, value: Any, ttl: Optional[int] = None
    ) -> bool:
        """
        Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (default: settings.cache_ttl_seconds)

        Returns:
            True if successful, False otherwise
        """
        if not self.enabled or not self.client:
            return False

        try:
            ttl = ttl or self.default_ttl
            serialized = json.dumps(value)
            await self.client.setex(key, ttl, serialized)
            logger.debug(f"Cache set: {key} (TTL: {ttl}s)")
            return True
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """
        Delete key from cache.

        Args:
            key: Cache key

        Returns:
            True if successful, False otherwise
        """
        if not self.enabled or not self.client:
            return False

        try:
            await self.client.delete(key)
            logger.debug(f"Cache delete: {key}")
            return True
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False

    async def clear_pattern(self, pattern: str) -> int:
        """
        Clear all keys matching a pattern.

        Args:
            pattern: Key pattern (e.g., 'ariba:*')

        Returns:
            Number of keys deleted
        """
        if not self.enabled or not self.client:
            return 0

        try:
            keys = []
            async for key in self.client.scan_iter(match=pattern):
                keys.append(key)

            if keys:
                deleted = await self.client.delete(*keys)
                logger.info(f"Cleared {deleted} keys matching '{pattern}'")
                return deleted
            return 0
        except Exception as e:
            logger.error(f"Cache clear pattern error: {e}")
            return 0

    async def get_or_set(
        self,
        key: str,
        factory_func,
        ttl: Optional[int] = None,
        *args,
        **kwargs,
    ) -> Any:
        """
        Get from cache or compute and set.

        Args:
            key: Cache key
            factory_func: Async function to compute value if cache miss
            ttl: Time to live in seconds
            *args: Arguments for factory_func
            **kwargs: Keyword arguments for factory_func

        Returns:
            Cached or computed value
        """
        # Try to get from cache
        cached_value = await self.get(key)
        if cached_value is not None:
            return cached_value

        # Compute value
        value = await factory_func(*args, **kwargs)

        # Store in cache
        await self.set(key, value, ttl)

        return value


# Global cache service instance
cache_service = CacheService()
