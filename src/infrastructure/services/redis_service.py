from datetime import datetime
import json
from typing import Any, Dict, Optional

from redis.asyncio import Redis

from src.configs.logger import log
from src.domain.constants.auth import TokenType
from src.domain.entities.auth import CachedToken
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
        expires_at = datetime.now().timestamp() + expiry  # Store as timestamp
        token_data = {
            "access_token": access_token,
            "expires_at": expires_at,
            "token_type": str(token_type)  # Convert enum to string
        }
        await self.set(key, token_data, expiry)

    async def get_cached_token(
        self,
        user_id: int,
        token_type: TokenType = TokenType.MICROSOFT
    ) -> Optional[CachedToken]:
        """Get cached token if exists and valid"""
        key = f"token:{token_type}:{user_id}"
        token_dict: Optional[Dict[str, Any]] = await self.get(key)
        log.info(f"Token dict: {token_dict}")

        if not token_dict:
            return None

        try:
            token_data = CachedToken(
                access_token=token_dict["access_token"],
                expires_at=float(token_dict["expires_at"]),  # Convert to float
                token_type=token_dict["token_type"]
            )

            if token_data.is_expired:
                await self.delete(key)
                return None

            return token_data

        except Exception as e:
            log.error(f"Error parsing cached token: {e}")
            await self.delete(key)
            return None

    async def delete_cached_token(
        self,
        user_id: int,
        token_type: TokenType
    ) -> None:
        """Delete cached token"""
        key = f"token:{token_type}:{user_id}"
        await self.delete(key)
