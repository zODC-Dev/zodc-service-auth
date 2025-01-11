from fastapi import BackgroundTasks

from src.domain.services.token_refresh_service import ITokenRefreshService


class TokenRefreshScheduler:
    def __init__(self, token_refresh_service: ITokenRefreshService):
        self.token_refresh_service = token_refresh_service

    async def schedule_refresh(self, background_tasks: BackgroundTasks, user_id: int):
        """Schedule token refresh in background"""
        background_tasks.add_task(
            self.token_refresh_service.schedule_token_refresh,
            user_id
        )
