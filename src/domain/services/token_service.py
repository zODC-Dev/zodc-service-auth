from abc import ABC, abstractmethod
from typing import Optional

from src.domain.entities.auth import AuthToken, UserIdentity


class ITokenService(ABC):
    @abstractmethod
    async def create_app_token(self, user: UserIdentity) -> AuthToken:
        """Create new access token"""
        pass

    @abstractmethod
    async def verify_token(self, token: str) -> Optional[UserIdentity]:
        """Verify token and return user identity"""
        pass

    @abstractmethod
    async def store_app_refresh_token(self, user_id: int, refresh_token: str) -> None:
        """Store refresh token"""
        pass
