# app/services/token_service.py
from redis.asyncio import Redis
from datetime import datetime, timedelta
import json
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.exceptions.auth import AuthException
from src.app.repositories.user_repository import user_repository
from src.configs.logger import logger
from src.configs.msal_config import msal_app
from src.configs.redis_config import get_redis_client

class TokenService:
    def __init__(self, redis_getter):
        self.redis = None
        self.redis_getter = redis_getter
        self.token_prefix = "msft_token:"
        self.expiry_time = 3500  # Slightly less than 1 hour

    async def initialize(self):
        """Initialize Redis client"""
        if self.redis is None:
            self.redis = await self.redis_getter()

    async def get_microsoft_token(self, user_id: int, db: AsyncSession) -> str:
        """Get a valid Microsoft access token for the user"""
        # Try to get from cache first
        cached_token = await self._get_cached_token(user_id)
        if cached_token:
            return cached_token

        # No valid cached token, need to refresh
        return await self._refresh_microsoft_token(user_id, db)

    async def _get_cached_token(self, user_id: int) -> Optional[str]:
        """Get token from cache if exists and valid"""
        await self.initialize()  # Ensure Redis client is initialized

        key = f"{self.token_prefix}{user_id}"
        token_data = await self.redis.get(key)
        
        if token_data:
            token_data = json.loads(token_data)
            expiry = datetime.fromisoformat(token_data['expiry'])
            
            # Return if token is still valid (not expired)
            if expiry > datetime.utcnow():
                return token_data['access_token']
                
        return None

    async def _refresh_microsoft_token(self, user_id: int, db: AsyncSession) -> str:
        """Refresh Microsoft access token using refresh token"""
        try:
            user = await user_repository.get_user_by_id(user_id, db)
            if not user or not user.microsoft_refresh_token:
                raise AuthException.INVALID_TOKEN

            # Use MSAL to refresh token
            result = await msal_app.acquire_token_by_refresh_token(
                user.microsoft_refresh_token,
                # scopes=["Calendars.Read, User.Read, Calendars.ReadWrite"]
                scopes=["User.Read"]
            )

            if "error" in result:
                raise AuthException.TOKEN_REFRESH_FAILED

            # Cache new token
            await self._cache_token(
                user_id,
                result['access_token'],
                datetime.utcnow() + timedelta(seconds=result['expires_in'])
            )

            # Update refresh token if provided
            if 'refresh_token' in result:
                await user_repository.update_refresh_token(
                    user_id,
                    result['refresh_token']
                )

            return result['access_token']

        except Exception as e:
            logger.error(f"Token refresh failed: {str(e)}")
            raise AuthException.TOKEN_REFRESH_FAILED

    async def _cache_token(self, user_id: int, access_token: str, expiry: datetime):
        """Cache access token with expiry"""
        await self.initialize()  # Ensure Redis client is initialized

        key = f"{self.token_prefix}{user_id}"
        token_data = {
            'access_token': access_token,
            'expiry': expiry.isoformat()
        }
        
        logger.info(f"Caching token for user {user_id}")
        await self.redis.setex(
            key,
            self.expiry_time,
            json.dumps(token_data)
        )

        logger.info(f"Token cached for user {user_id}")

token_service = TokenService(get_redis_client)