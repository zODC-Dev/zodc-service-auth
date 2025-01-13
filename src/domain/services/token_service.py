from abc import ABC, abstractmethod
from typing import Optional

from sqlmodel.ext.asyncio.session import AsyncSession

from src.domain.entities.auth import TokenPair
from src.domain.entities.user import User


class ITokenService(ABC):
    @abstractmethod
    async def create_token_pair(self, user: User) -> TokenPair:
        """Create new access and refresh token pair"""
        pass

    @abstractmethod
    async def refresh_tokens(self, refresh_token: str) -> TokenPair:
        """Refresh access token using refresh token"""
        pass

    @abstractmethod
    async def verify_token(self, token: str) -> Optional[User]:
        """Verify token and return user identity"""
        pass

    @abstractmethod
    async def get_microsoft_token(self, user_id: int, db: AsyncSession) -> str:
        """Get Microsoft token for user"""
        pass

    @abstractmethod
    async def get_valid_microsoft_token(self, user_id: int) -> str:
        """Get valid Microsoft token, refreshing if necessary"""
        pass

    @abstractmethod
    async def get_valid_jira_token(self, user_id: int) -> str:
        """Get valid Jira token, refreshing if necessary"""
        pass
