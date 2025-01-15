from datetime import datetime, timedelta
import json
from typing import Any, Dict, Optional

from redis.asyncio import Redis

from src.domain.constants.auth import TokenType
from src.domain.services.redis_service import IRedisService


class RedisService(IRedisService):
    """Service for managing Redis operations."""

    def __init__(self, redis_client: Redis):
        self.redis = redis_client

    async def get(self, key: str) -> Optional[Any]:
        """Get a value from Redis by key."""
        value = await self.redis.get(key)
        if value:
            return json.loads(value)
        return None

    async def set(self, key: str, value: Dict[str, Any], expiry: int) -> None:
        """Set a value in Redis with an expiry time."""
        await self.redis.setex(key, expiry, json.dumps(value, default=str))

    async def delete(self, key: str) -> None:
        """Delete a key from Redis."""
        await self.redis.delete(key)

    async def cache_token(
        self,
        user_id: int,
        access_token: str,
        expiry: int,
        token_type: TokenType = TokenType.MICROSOFT
    ) -> None:
        """Cache access token with expiry"""
        key = f"token:{token_type}:{user_id}"
        token_data = {
            "access_token": access_token,
            "expires_at": (datetime.now() + timedelta(seconds=expiry)).timestamp(),
            "token_type": token_type
        }
        await self.set(key, token_data, expiry)

    async def get_cached_token(
        self,
        user_id: int,
        token_type: TokenType = TokenType.MICROSOFT
    ) -> Optional[str]:
        """Get cached token if exists and valid"""
        key = f"token:{token_type}:{user_id}"
        token_str: Optional[str] = await self.get(key)
        if not token_str:
            return None
        token_data: Dict[str, Any] = json.loads(token_str)

        if token_data:
            return token_data.get("access_token")
        return None

    async def delete_cached_token(
        self,
        user_id: int,
        token_type: TokenType
    ) -> None:
        """Delete cached token"""
        key = f"token:{token_type}:{user_id}"
        await self.delete(key)
