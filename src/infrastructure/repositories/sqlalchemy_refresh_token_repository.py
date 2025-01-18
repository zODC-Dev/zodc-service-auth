from datetime import datetime
from typing import Optional

from sqlmodel import and_, col, select, update
from sqlmodel.ext.asyncio.session import AsyncSession

from src.domain.constants.auth import TokenType
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
            is_revoked=refresh_token.is_revoked,
            token_type=refresh_token.token_type
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

    async def get_by_user_id_and_type(self, user_id: int, token_type: TokenType) -> Optional[RefreshTokenEntity]:
        """Get refresh token by user id and token type by last created"""
        result = await self.session.exec(
            select(RefreshTokenModel).where(
                and_(
                    RefreshTokenModel.user_id == user_id,
                    RefreshTokenModel.token_type == token_type
                )
            ).order_by(col(RefreshTokenModel.created_at).desc())
        )
        db_token = result.first()
        return self._to_domain(db_token) if db_token else None

    async def revoke_tokens_by_user_and_type(self, user_id: int, token_type: TokenType) -> None:
        """Revoke all tokens of a specific type for a user"""
        stmt = (
            update(RefreshTokenModel)
            .where(
                and_(
                    RefreshTokenModel.user_id == user_id,
                    RefreshTokenModel.token_type == token_type,
                    RefreshTokenModel.is_revoked == False  # noqa: E712
                )
            )
            .values(is_revoked=True)
        )
        await self.session.exec(stmt)  # type: ignore
        await self.session.commit()

    async def cleanup_expired_tokens(self) -> None:
        """Clean up expired tokens by marking them as revoked"""
        stmt = (
            update(RefreshTokenModel)
            .where(
                and_(
                    RefreshTokenModel.expires_at < datetime.now(),
                    RefreshTokenModel.is_revoked == False  # noqa: E712
                )
            )
            .values(is_revoked=True)
        )
        await self.session.exec(stmt)  # type: ignore
        await self.session.commit()

    def _to_domain(self, db_token: RefreshTokenModel) -> RefreshTokenEntity:
        return RefreshTokenEntity(
            token=db_token.token,
            user_id=db_token.user_id,
            expires_at=db_token.expires_at,
            is_revoked=db_token.is_revoked,
            created_at=db_token.created_at,
            token_type=db_token.token_type
        )
