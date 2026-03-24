"""
Redis Cache Service
Provides caching layer for improved performance and reduced database load
"""
import json
import hashlib
from typing import Optional, Any, List
from functools import wraps
from datetime import timedelta
from core.logging import get_logger
from core.config import settings

logger = get_logger(__name__)

# Try to import redis - if not available, use in-memory fallback
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logger.warning("Redis not available, using in-memory cache fallback")


class CacheService:
    """Redis-based caching service with in-memory fallback"""

    def __init__(self):
        self.enabled = settings.ENABLE_CACHE and REDIS_AVAILABLE
        self.redis_client = None
        self.memory_cache = {}  # Fallback in-memory cache

        if self.enabled:
            try:
                self.redis_client = redis.from_url(
                    settings.REDIS_URL,
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5
                )
                # Test connection
                self.redis_client.ping()
                logger.info(f"Redis cache enabled: {settings.REDIS_URL}")
            except Exception as e:
                logger.warning(f"Redis connection failed: {e}, using in-memory cache")
                self.enabled = False
        else:
            cache_type = "in-memory" if not REDIS_AVAILABLE else "disabled"
            logger.info(f"Cache: {cache_type}")

    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate cache key from prefix and arguments"""
        # Create a hash of the arguments for consistent keys
        key_parts = [prefix] + [str(arg) for arg in args] + [f"{k}={v}" for k, v in sorted(kwargs.items())]
        key_string = ":".join(key_parts)

        # Hash long keys to avoid Redis key length limits
        if len(key_string) > 100:
            key_hash = hashlib.md5(key_string.encode()).hexdigest()[:8]
            return f"{prefix}:{key_hash}"

        return key_string

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            if self.enabled and self.redis_client:
                value = self.redis_client.get(key)
                if value:
                    return json.loads(value)
            else:
                # In-memory fallback
                if key in self.memory_cache:
                    return self.memory_cache[key]
            return None
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Set value in cache

        Args:
            key: Cache key
            value: Value to cache (must be JSON serializable)
            ttl: Time to live in seconds (defaults to settings.CACHE_TTL)

        Returns:
            True if successful
        """
        try:
            ttl = ttl or settings.CACHE_TTL
            serialized = json.dumps(value, default=str)

            if self.enabled and self.redis_client:
                self.redis_client.setex(key, ttl, serialized)
            else:
                # In-memory fallback with simple TTL
                import time
                self.memory_cache[key] = {
                    "value": value,
                    "expires": time.time() + ttl
                }
                # Clean expired entries periodically
                if len(self.memory_cache) > 1000:
                    self._clean_memory_cache()

            return True
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        try:
            if self.enabled and self.redis_client:
                self.redis_client.delete(key)
            else:
                if key in self.memory_cache:
                    del self.memory_cache[key]
            return True
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            return False

    async def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern"""
        try:
            if self.enabled and self.redis_client:
                keys = self.redis_client.keys(pattern)
                if keys:
                    return self.redis_client.delete(*keys)
                return 0
            else:
                # In-memory: delete keys that start with pattern
                keys_to_delete = [k for k in self.memory_cache.keys() if k.startswith(pattern)]
                for key in keys_to_delete:
                    del self.memory_cache[key]
                return len(keys_to_delete)
        except Exception as e:
            logger.error(f"Cache delete_pattern error for {pattern}: {e}")
            return 0

    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        try:
            if self.enabled and self.redis_client:
                return bool(self.redis_client.exists(key))
            else:
                # Check in-memory cache and expiration
                if key in self.memory_cache:
                    import time
                    entry = self.memory_cache[key]
                    if isinstance(entry, dict) and "expires" in entry:
                        if time.time() > entry["expires"]:
                            del self.memory_cache[key]
                            return False
                    return True
                return False
        except Exception as e:
            logger.error(f"Cache exists error for key {key}: {e}")
            return False

    def _clean_memory_cache(self):
        """Clean expired entries from in-memory cache"""
        import time
        current_time = time.time()
        expired_keys = [
            k for k, v in self.memory_cache.items()
            if isinstance(v, dict) and "expires" in v and current_time > v["expires"]
        ]
        for key in expired_keys:
            del self.memory_cache[key]
        logger.debug(f"Cleaned {len(expired_keys)} expired cache entries")

    async def clear_all(self) -> bool:
        """Clear all cache (use with caution)"""
        try:
            if self.enabled and self.redis_client:
                self.redis_client.flushdb()
            else:
                self.memory_cache.clear()
            logger.info("Cache cleared")
            return True
        except Exception as e:
            logger.error(f"Cache clear error: {e}")
            return False

    def get_cache_stats(self) -> dict:
        """Get cache statistics"""
        try:
            if self.enabled and self.redis_client:
                info = self.redis_client.info()
                return {
                    "type": "redis",
                    "enabled": True,
                    "keys": info.get("db0", {}).get("keys", 0),
                    "memory_used": info.get("used_memory_human", "N/A"),
                    "hit_rate": info.get("keyspace_hits", 0) / max(info.get("keyspace_hits", 0) + info.get("keyspace_misses", 0), 1) * 100
                }
            else:
                return {
                    "type": "memory",
                    "enabled": False,
                    "keys": len(self.memory_cache),
                    "memory_used": "N/A",
                    "hit_rate": "N/A"
                }
        except Exception as e:
            logger.error(f"Cache stats error: {e}")
            return {"type": "unknown", "enabled": False, "error": str(e)}


# Global cache service instance
cache = CacheService()


def cache_response(
    prefix: str,
    ttl: Optional[int] = None,
    include_user_id: bool = False
):
    """
    Decorator to cache function responses

    Args:
        prefix: Cache key prefix
        ttl: Time to live in seconds
        include_user_id: Include user_id in cache key (from kwargs)

    Usage:
        @cache_response("products", ttl=300)
        async def get_products(category: str, db: Session = Depends(get_db)):
            ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            key_parts = [prefix]

            # Add user_id if needed
            if include_user_id and "current_user" in kwargs:
                key_parts.append(f"user_{kwargs['current_user'].id}")

            # Add other args to key
            cache_key = cache._generate_key(*key_parts, *args[1:], **kwargs)

            # Try to get from cache
            cached_value = await cache.get(cache_key)
            if cached_value is not None:
                logger.debug(f"Cache hit: {cache_key}")
                return cached_value

            # Call function and cache result
            result = await func(*args, **kwargs)
            await cache.set(cache_key, result, ttl=ttl)
            logger.debug(f"Cache set: {cache_key}")

            return result

        return wrapper
    return decorator


async def invalidate_cache_pattern(pattern: str) -> int:
    """
    Invalidate all cache entries matching pattern

    Usage:
        await invalidate_cache_pattern("products:*")
    """
    count = await cache.delete_pattern(pattern)
    logger.info(f"Invalidated {count} cache entries matching {pattern}")
    return count


async def invalidate_product_cache(product_id: Optional[int] = None):
    """Invalidate product-related cache entries"""
    patterns = ["products:*", "product:*"]

    if product_id:
        patterns.append(f"product:{product_id}:*")

    for pattern in patterns:
        await cache.delete_pattern(pattern)


async def invalidate_order_cache(user_id: Optional[int] = None):
    """Invalidate order-related cache entries"""
    patterns = ["orders:*"]

    if user_id:
        patterns.append(f"orders:user_{user_id}:*")

    for pattern in patterns:
        await cache.delete_pattern(pattern)


async def invalidate_user_cache(user_id: int):
    """Invalidate user-specific cache entries"""
    patterns = [
        f"user:{user_id}:*",
        f"orders:user_{user_id}:*",
        f"products:seller_{user_id}:*"
    ]

    for pattern in patterns:
        await cache.delete_pattern(pattern)
