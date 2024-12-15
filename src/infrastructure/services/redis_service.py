from datetime import datetime
import json
from typing import Any, Dict

from redis.asyncio import Redis

from src.configs.logger import logger


class RedisService:
    """Service for managing Redis operations."""

    def __init__(self, redis_client: Redis):
        self.redis = redis_client

    async def get(self, key: str) -> Any:
        """Get a value from Redis by key."""
        value = await self.redis.get(key)
        if value:
            return json.loads(value)
        return None

    async def set(self, key: str, value: Dict[str, Any], expiry: int):
        """Set a value in Redis with an expiry time."""
        await self.redis.setex(key, expiry, json.dumps(value))

    async def delete(self, key: str):
        """Delete a key from Redis."""
        await self.redis.delete(key)

    async def cache_token(self, user_id: int, access_token: str, expiry: int):
        """Cache microsoft access token with expiry."""
        try:
            key = f"msft_token:{user_id}"
            token_data = {"access_token": access_token, "expiry": expiry}
            await self.set(key, token_data, expiry)
        except Exception as e:
            logger.error(f"{str(e)}")

    async def get_cached_token(self, user_id: int) -> str:
        """Get microsoft access token from cache if exists and valid."""
        key = f"msft_token:{user_id}"
        token_data = await self.get(key)
        if token_data:
            expiry = datetime.fromisoformat(token_data["expiry"])
            if expiry > datetime.now():
                access_token: str = token_data.get("access_token", "")
                return access_token
        return ""
