from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from aiohttp import ClientSession

from src.configs.logger import log
from src.configs.settings import settings
from src.domain.constants.auth import TokenType
from src.domain.exceptions.auth_exceptions import UserNotFoundError
from src.domain.repositories.user_repository import IUserRepository
from src.domain.services.redis_service import IRedisService
from src.domain.services.token_refresh_service import ITokenRefreshService


class TokenRefreshService(ITokenRefreshService):
    def __init__(
        self,
        redis_service: IRedisService,
        user_repository: IUserRepository
    ):
        self.redis_service = redis_service
        self.user_repository = user_repository

    async def refresh_microsoft_token(self, user_id: int) -> Optional[str]:
        """Refresh Microsoft access token"""
        try:
            user = await self.user_repository.get_user_by_id(user_id)
            if not user or not user.microsoft_refresh_token:
                return None

            # Exchange refresh token for new access token
            async with ClientSession() as session:
                response = await session.post(
                    "https://login.microsoftonline.com/common/oauth2/v2.0/token",
                    data={
                        "client_id": settings.CLIENT_AZURE_CLIENT_ID,
                        "refresh_token": user.microsoft_refresh_token,
                        "grant_type": "refresh_token",
                        "scope": "User.Read email profile offline_access"
                    }
                )
                data: Dict[str, str] = await response.json()

                if "error" in data:
                    log.error(f"Microsoft token refresh failed: {data}")
                    return None

                # Update user and cache new token
                if user.id is None:
                    raise UserNotFoundError("User not found")
                await self._update_microsoft_tokens(user.id, data)
                return data.get("access_token")

        except Exception as e:
            log.error(f"Error refreshing Microsoft token: {str(e)}")
            return None

    async def refresh_jira_token(self, user_id: int) -> Optional[str]:
        """Refresh Jira access token"""
        try:
            user = await self.user_repository.get_user_by_id(user_id)
            if not user or not user.jira_refresh_token:
                return None

            # Exchange refresh token for new access token
            async with ClientSession() as session:
                response = await session.post(
                    "https://auth.atlassian.com/oauth/token",
                    data={
                        "grant_type": "refresh_token",
                        "client_id": settings.JIRA_CLIENT_ID,
                        "client_secret": settings.JIRA_CLIENT_SECRET,
                        "refresh_token": user.jira_refresh_token
                    }
                )
                data: Dict[str, str] = await response.json()

                if "error" in data:
                    log.error(f"Jira token refresh failed: {data}")
                    return None

                # Update user and cache new token
                assert user.id is not None
                await self._update_jira_tokens(user.id, data)
                return data.get("access_token")

        except Exception as e:
            log.error(f"Error refreshing Jira token: {str(e)}")
            return None

    async def schedule_token_refresh(self, user_id: int) -> None:
        """Schedule token refresh for a user"""
        user = await self.user_repository.get_user_by_id(user_id)
        if not user:
            return

        now = datetime.now()
        refresh_threshold = timedelta(minutes=5)

        # Check and refresh Microsoft token
        if (user.microsoft_token_expires_at and
                user.microsoft_token_expires_at - now <= refresh_threshold):
            await self.refresh_microsoft_token(user_id)

        # Check and refresh Jira token
        if (user.jira_token_expires_at and
                user.jira_token_expires_at - now <= refresh_threshold):
            await self.refresh_jira_token(user_id)

    async def _update_microsoft_tokens(self, user_id: int, token_data: Dict[str, Any]) -> None:
        """Update Microsoft tokens in database and cache"""
        user = await self.user_repository.get_user_by_id(user_id)
        if user:
            user.microsoft_access_token = token_data["access_token"]
            if "refresh_token" in token_data:
                user.microsoft_refresh_token = token_data["refresh_token"]
            user.microsoft_token_expires_at = datetime.now() + timedelta(seconds=token_data["expires_in"])
            await self.user_repository.update_user_by_id(user_id, user)

        await self.redis_service.cache_token(
            user_id=user_id,
            access_token=token_data["access_token"],
            expiry=token_data["expires_in"],
            token_type=TokenType.MICROSOFT
        )

    async def _update_jira_tokens(self, user_id: int, token_data: Dict[str, Any]) -> None:
        """Update Jira tokens in database and cache"""
        user = await self.user_repository.get_user_by_id(user_id)
        if user:
            user.jira_access_token = token_data["access_token"]
            if "refresh_token" in token_data:
                user.jira_refresh_token = token_data["refresh_token"]
            user.jira_token_expires_at = datetime.now() + timedelta(seconds=token_data["expires_in"])
            await self.user_repository.update_user_by_id(user_id, user)

        await self.redis_service.cache_token(
            user_id=user_id,
            access_token=token_data["access_token"],
            expiry=token_data["expires_in"],
            token_type=TokenType.JIRA
        )
