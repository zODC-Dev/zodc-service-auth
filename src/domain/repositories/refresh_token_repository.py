from abc import ABC, abstractmethod
from typing import Optional

from src.domain.entities.auth import RefreshTokenEntity


class IRefreshTokenRepository(ABC):
    @abstractmethod
    async def create_refresh_token(self, refresh_token: RefreshTokenEntity) -> RefreshTokenEntity:
        """Create new refresh token"""
        pass

    @abstractmethod
    async def get_by_token(self, token: str) -> Optional[RefreshTokenEntity]:
        """Get refresh token by token string"""
        pass

    @abstractmethod
    async def revoke_token(self, token: str) -> None:
        """Revoke a refresh token"""
        pass
