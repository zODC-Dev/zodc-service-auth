from datetime import datetime, timedelta
import secrets
from typing import Optional

import jwt
from sqlmodel import col, select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.configs.logger import log
from src.configs.settings import settings
from src.domain.constants.auth import TokenType
from src.domain.entities.auth import RefreshTokenEntity, TokenPair
from src.domain.entities.user import User as UserEntity
from src.domain.exceptions.auth_exceptions import InvalidTokenError, TokenError, TokenExpiredError
from src.domain.repositories.refresh_token_repository import IRefreshTokenRepository
from src.domain.repositories.role_repository import IRoleRepository
from src.domain.repositories.user_repository import IUserRepository
from src.domain.services.redis_service import IRedisService
from src.domain.services.token_refresh_service import ITokenRefreshService
from src.domain.services.token_service import ITokenService
from src.infrastructure.models.refresh_token import RefreshToken as RefreshTokenModel


class JWTTokenService(ITokenService):
    def __init__(
        self,
        redis_service: IRedisService,
        role_repository: IRoleRepository,
        user_repository: IUserRepository,
        refresh_token_repository: IRefreshTokenRepository,
        token_refresh_service: ITokenRefreshService
    ):
        self.redis_service = redis_service
        self.role_repository = role_repository
        self.user_repository = user_repository
        self.refresh_token_repository = refresh_token_repository
        self.token_refresh_service = token_refresh_service

    async def create_token_pair(self, user: UserEntity) -> TokenPair:
        """Create new access and refresh token pair"""
        try:
            # Create access token
            access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token_expires_at = datetime.now() + access_token_expires

            access_token = jwt.encode(
                {
                    "sub": str(user.id),
                    "email": user.email,
                    "name": user.name,
                    "exp": access_token_expires_at
                },
                settings.JWT_SECRET,
                algorithm=settings.JWT_ALGORITHM
            )

            # Create refresh token
            refresh_token = secrets.token_urlsafe(64)
            refresh_token_expires = timedelta(seconds=settings.REFRESH_TOKEN_EXPIRATION_TIME)
            refresh_token_expires_at = datetime.now() + refresh_token_expires

            # Store refresh token
            await self.refresh_token_repository.create_refresh_token(
                RefreshTokenEntity(
                    token=refresh_token,
                    user_id=user.id,
                    expires_at=refresh_token_expires_at,
                    token_type=TokenType.APP
                )
            )

            return TokenPair(
                access_token=access_token,
                refresh_token=refresh_token,
                token_type="bearer",
                expires_in=int(access_token_expires.total_seconds())
            )

        except Exception as e:
            log.error(f"Token creation error: {str(e)}")
            raise TokenError("Failed to create tokens") from e

    async def refresh_tokens(self, refresh_token: str) -> TokenPair:
        """Refresh access token using refresh token"""
        try:
            # Get refresh token from database
            stored_token = await self.refresh_token_repository.get_by_token(refresh_token)
            if not stored_token:
                raise InvalidTokenError("Invalid refresh token")

            # Check if token is expired or revoked
            if stored_token.is_revoked:
                raise InvalidTokenError("Refresh token has been revoked")
            if stored_token.expires_at < datetime.now():
                raise TokenExpiredError("Refresh token has expired")

            # Get user
            user = await self.user_repository.get_user_by_id(stored_token.user_id)
            if not user:
                raise InvalidTokenError("User not found")

            # Revoke old refresh token
            await self.refresh_token_repository.revoke_token(refresh_token)

            # Create new token pair
            return await self.create_token_pair(user)
        except Exception as e:
            log.error(f"Token refresh error: {str(e)}")
            raise TokenError("Failed to refresh tokens") from e

    async def verify_token(self, token: str) -> Optional[UserEntity]:
        """Verify JWT token"""
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET,
                algorithms=[settings.JWT_ALGORITHM]
            )

            # From payload, get user_id, email, name
            user_id = payload.get("sub")

            if not user_id:
                raise InvalidTokenError("Invalid token")

            # Use user_id to get user from database
            user = await self.user_repository.get_user_by_id_with_role_permissions(user_id)

            if not user:
                raise InvalidTokenError("User not found")

            return user
        except jwt.ExpiredSignatureError as e:
            raise TokenExpiredError() from e
        except jwt.InvalidTokenError as e:
            raise InvalidTokenError() from e
        except Exception as e:
            log.error(f"Error verifying token: {str(e)}")
            raise TokenError("Failed to verify token") from e

    async def get_microsoft_token(self, user_id: int, db: AsyncSession) -> str:
        """Get Microsoft access token for user"""
        cached_token = await self.redis_service.get_cached_token(user_id, TokenType.MICROSOFT)
        if cached_token:
            return cached_token

        # Logic to retrieve from the database if not cached
        try:
            result = await db.exec(
                select(RefreshTokenModel.token).where(
                    RefreshTokenModel.user_id == user_id,
                    RefreshTokenModel.token_type == TokenType.MICROSOFT
                ).order_by(col(RefreshTokenModel.created_at).desc())
            )
            db_token = result.one_or_none()
            if not db_token:
                raise TokenError("Microsoft token not found")
            return db_token
        except Exception as e:
            log.error(f"Error getting Microsoft token: {str(e)}")
            raise TokenError("Failed to get Microsoft token") from e

    async def get_valid_microsoft_token(self, user_id: int) -> str:
        """Get valid Microsoft token"""
        # Try to get from cache first
        token = await self.redis_service.get_cached_token(user_id, TokenType.MICROSOFT)
        if token:
            return token

        # If not in cache, refresh token
        new_token = await self.token_refresh_service.refresh_microsoft_token(user_id)
        if not new_token:
            raise TokenError("Failed to get valid Microsoft token")

        # Cache new token
        await self.redis_service.cache_token(user_id, new_token, settings.MICROSOFT_TOKEN_EXPIRATION_TIME, TokenType.MICROSOFT)

        return new_token

    async def get_valid_jira_token(self, user_id: int) -> str:
        """Get valid Jira token"""
        # Try to get from cache first
        token = await self.redis_service.get_cached_token(user_id, TokenType.JIRA)
        if token:
            return token

        # If not in cache, refresh token
        new_token = await self.token_refresh_service.refresh_jira_token(user_id)
        if not new_token:
            raise TokenError("Failed to get valid Jira token")

        # Cache new token
        await self.redis_service.cache_token(user_id, new_token, settings.JIRA_TOKEN_EXPIRATION_TIME, TokenType.JIRA)

        return new_token
