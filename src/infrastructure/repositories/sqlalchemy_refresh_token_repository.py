from typing import Optional

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.domain.entities.auth import RefreshTokenEntity
from src.domain.repositories.refresh_token_repository import IRefreshTokenRepository
from src.infrastructure.models.refresh_token import RefreshToken as RefreshTokenModel


class SQLAlchemyRefreshTokenRepository(IRefreshTokenRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_refresh_token(self, refresh_token: RefreshTokenEntity) -> RefreshTokenEntity:
        db_token = RefreshTokenModel(
            token=refresh_token.token,
            user_id=refresh_token.user_id,
            expires_at=refresh_token.expires_at,
            is_revoked=refresh_token.is_revoked
        )
        self.session.add(db_token)
        await self.session.commit()
        await self.session.refresh(db_token)
        return self._to_domain(db_token)

    async def get_by_token(self, token: str) -> Optional[RefreshTokenEntity]:
        result = await self.session.exec(
            select(RefreshTokenModel).where(RefreshTokenModel.token == token)
        )
        db_token = result.first()
        return self._to_domain(db_token) if db_token else None

    async def revoke_token(self, token: str) -> None:
        result = await self.session.exec(
            select(RefreshTokenModel).where(RefreshTokenModel.token == token)
        )
        db_token = result.first()
        if db_token:
            db_token.is_revoked = True
            await self.session.commit()

    def _to_domain(self, db_token: RefreshTokenModel) -> RefreshTokenEntity:
        return RefreshTokenEntity(
            token=db_token.token,
            user_id=db_token.user_id,
            expires_at=db_token.expires_at,
            is_revoked=db_token.is_revoked,
            created_at=db_token.created_at
        )
