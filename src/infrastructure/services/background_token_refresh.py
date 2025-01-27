from datetime import datetime, timedelta, timezone

from fastapi import BackgroundTasks

from src.domain.repositories.user_repository import IUserRepository
from src.domain.services.token_refresh_service import ITokenRefreshService


class BackgroundTokenRefresh:
    def __init__(
        self,
        token_refresh_service: ITokenRefreshService,
        user_repository: IUserRepository
    ):
        self.token_refresh_service = token_refresh_service
        self.user_repository = user_repository

    async def schedule_token_refresh(self, background_tasks: BackgroundTasks, user_id: int):
        """Schedule token refresh for a user"""
        background_tasks.add_task(self._refresh_tokens, user_id)

    async def _refresh_tokens(self, user_id: int):
        """Refresh all tokens for a user if needed"""
        user = await self.user_repository.get_user_by_id(user_id)
        if not user:
            return

        now = datetime.now(timezone.utc)
        refresh_threshold = timedelta(minutes=5)

        # Check and refresh Microsoft token
        if (user.microsoft_token_expires_at and
                user.microsoft_token_expires_at - now <= refresh_threshold):
            await self.token_refresh_service.refresh_microsoft_token(user_id)

        # Check and refresh Jira token
        if (user.jira_token_expires_at and
                user.jira_token_expires_at - now <= refresh_threshold):
            await self.token_refresh_service.refresh_jira_token(user_id)
