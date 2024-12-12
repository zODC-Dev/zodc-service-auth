import json
from datetime import datetime

from redis.asyncio import Redis

from src.configs.logger import logger


class RedisService:
    """Service for managing Redis operations."""

    def __init__(self, redis_client: Redis):
        self.redis = redis_client

    async def get(self, key: str) -> dict:
        """Get a value from Redis by key."""
        token_data = await self.redis.get(key)
        if token_data:
            return json.loads(token_data)
        return None

    async def set(self, key: str, value: dict, expiry: int):
        """Set a value in Redis with an expiry time."""
        await self.redis.setex(key, expiry, json.dumps(value))

    async def delete(self, key: str):
        """Delete a key from Redis."""
        await self.redis.delete(key)

    async def cache_token(self, user_id: int, access_token: str, expiry: datetime):
        """Cache microsoft access token with expiry."""
        try:
            key = f"msft_token:{user_id}"
            token_data = {"access_token": access_token, "expiry": expiry.isoformat()}
            await self.set(key, token_data, expiry.timestamp() - datetime.now().timestamp())
        except Exception as e:
            logger.error(f"{str(e)}")

    async def get_cached_token(self, user_id: int) -> str:
        """Get microsoft access token from cache if exists and valid."""
        key = f"msft_token:{user_id}"
        token_data = await self.get(key)
        if token_data:
            expiry = datetime.fromisoformat(token_data["expiry"])
            if expiry > datetime.now():
                return token_data["access_token"]
        return None
