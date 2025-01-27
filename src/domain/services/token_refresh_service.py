from abc import ABC, abstractmethod
from typing import Optional


class ITokenRefreshService(ABC):
    @abstractmethod
    async def refresh_microsoft_token(self, user_id: int) -> Optional[str]:
        """Refresh Microsoft access token using refresh token"""
        pass

    @abstractmethod
    async def refresh_jira_token(self, user_id: int) -> Optional[str]:
        """Refresh Jira access token using refresh token"""
        pass

    @abstractmethod
    async def schedule_token_refresh(self, user_id: int) -> None:
        """Schedule token refresh for a user"""
        pass
