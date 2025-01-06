from datetime import datetime, timedelta
from typing import Optional

import jwt
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.configs.logger import log
from src.configs.settings import settings
from src.domain.entities.auth import AuthToken
from src.domain.entities.user import User as UserEntity
from src.domain.exceptions.auth_exceptions import InvalidTokenError, TokenError, TokenExpiredError
from src.domain.repositories.role_repository import IRoleRepository
from src.domain.repositories.user_repository import IUserRepository
from src.domain.services.redis_service import IRedisService
from src.domain.services.token_service import ITokenService
from src.infrastructure.models.user import User as UserModel


class JWTTokenService(ITokenService):
    def __init__(self, redis_service: IRedisService, role_repository: IRoleRepository, user_repository: IUserRepository):
        self.redis_service = redis_service
        self.role_repository = role_repository
        self.user_repository = user_repository

    async def create_app_token(self, user: UserEntity) -> AuthToken:
        """Create new JWT token"""
        try:
            expires_delta = timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            expires_at = datetime.now() + expires_delta

            if user.id is None:
                raise TokenError("User not exist")

            claims = {
                "sub": str(user.id),
                "email": user.email,
                "name": user.name,
                "exp": expires_at
            }

            access_token = jwt.encode(
                claims,
                settings.JWT_SECRET,
                algorithm=settings.JWT_ALGORITHM
            )

            return AuthToken(
                access_token=access_token,
                expires_at=expires_at
            )
        except Exception as e:
            log.error(f"Token creation error: {str(e)}")
            raise TokenError("Failed to create token") from e

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
        cached_token = await self.redis_service.get_cached_token(user_id)
        if cached_token:
            return cached_token

        # Logic to retrieve from the database if not cached
        try:
            result = await db.exec(
                select(UserModel.microsoft_token).where(
                    UserModel.id == user_id)
            )
            db_token = result.one_or_none()
            if not db_token:
                raise TokenError("Microsoft token not found")
            return db_token
        except Exception as e:
            log.error(f"Error getting Microsoft token: {str(e)}")
            raise TokenError("Failed to get Microsoft token") from e

    async def store_app_refresh_token(self, user_id: int, refresh_token: str) -> None:
        """Store refresh token"""
        # Implementation for storing refresh token into database
        pass

    async def store_microsoft_refresh_token(self, user_id, microsoft_refresh_token: str) -> None:
        """Store microsoft refresh token"""
        pass

    async def refresh_microsoft_token(self, user_id: int, db: AsyncSession) -> str:
        """Refresh Microsoft access token if needed"""
        # Implementation for refreshing Microsoft token
        return ""
