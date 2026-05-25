"""
Redis client for token blacklisting and caching.
"""

import redis.asyncio as aioredis
from app.core.config import settings

# Single shared Redis connection pool
redis_client: aioredis.Redis = aioredis.from_url(
    settings.REDIS_URL,
    encoding="utf-8",
    decode_responses=True,
)


async def blacklist_token(token: str, ttl_seconds: int) -> None:
    """Add a token to the blacklist with automatic expiry."""
    await redis_client.setex(f"blacklist:{token}", ttl_seconds, "1")


async def is_token_blacklisted(token: str) -> bool:
    """Check if a token has been blacklisted (user logged out)."""
    result = await redis_client.get(f"blacklist:{token}")
    return result is not None


async def close_redis() -> None:
    await redis_client.aclose()