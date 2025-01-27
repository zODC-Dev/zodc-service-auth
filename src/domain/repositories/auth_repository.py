from abc import ABC, abstractmethod
from typing import Optional

from src.domain.constants.auth import TokenType
from src.domain.entities.auth import MicrosoftIdentity, UserCredentials
from src.domain.entities.user import User


class IAuthRepository(ABC):
    @abstractmethod
    async def create_sso_user(self, microsoft_identity: MicrosoftIdentity) -> User:
        """Create new user"""
        pass

    @abstractmethod
    async def update_refresh_token(self, user_id: int, refresh_token: str, token_type: TokenType) -> None:
        """Update user's refresh token"""
        pass

    @abstractmethod
    async def verify_credentials(self, credentials: UserCredentials) -> Optional[User]:
        """Verify user credentials"""
        pass
