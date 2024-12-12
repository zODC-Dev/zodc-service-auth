from abc import ABC, abstractmethod
from typing import Optional

from src.domain.entities.auth import MicrosoftIdentity, UserCredentials, UserIdentity


class IAuthRepository(ABC):
    @abstractmethod
    async def create_sso_user(self, microsoft_identity: MicrosoftIdentity) -> UserIdentity:
        """Create new user"""
        pass

    @abstractmethod
    async def update_refresh_token(self, user_id: int, refresh_token: str) -> None:
        """Update user's refresh token"""
        pass

    @abstractmethod
    async def verify_credentials(self, credentials: UserCredentials) -> Optional[UserIdentity]:
        """Verify user credentials"""
        pass
