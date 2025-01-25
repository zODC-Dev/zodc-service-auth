from datetime import datetime, timedelta
from pathlib import Path
import secrets
from typing import Dict, List, Optional, cast

import jwt
from sqlmodel import col, select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.configs.logger import log
from src.configs.settings import settings
from src.domain.constants.auth import TokenType
from src.domain.entities.auth import CachedToken, RefreshTokenEntity, TokenPair
from src.domain.entities.user import User as UserEntity
from src.domain.exceptions.auth_exceptions import InvalidTokenError, TokenError, TokenExpiredError
from src.domain.repositories.permission_repository import IPermissionRepository
from src.domain.repositories.refresh_token_repository import IRefreshTokenRepository
from src.domain.repositories.role_repository import IRoleRepository
from src.domain.repositories.user_repository import IUserRepository
from src.domain.services.redis_service import IRedisService
from src.domain.services.token_refresh_service import ITokenRefreshService
from src.domain.services.token_service import ITokenService
from src.domain.value_objects.token import TokenPayload
from src.infrastructure.models.refresh_token import RefreshToken as RefreshTokenModel


class JWTTokenService(ITokenService):
    _private_key: bytes
    _public_key: bytes

    def __init__(
        self,
        redis_service: IRedisService,
        role_repository: IRoleRepository,
        user_repository: IUserRepository,
        refresh_token_repository: IRefreshTokenRepository,
        token_refresh_service: ITokenRefreshService,
        permission_repository: IPermissionRepository
    ):
        self.redis_service = redis_service
        self.role_repository = role_repository
        self.user_repository = user_repository
        self.refresh_token_repository = refresh_token_repository
        self.token_refresh_service = token_refresh_service
        self.permission_repository = permission_repository

        self._load_keys()

    async def create_token_pair(self, user: UserEntity) -> TokenPair:
        """Create new access and refresh token pair"""
        try:
            if not user.id:
                raise ValueError("User ID is required")
            # Get user's roles and permissions
            system_role = await self.role_repository.get_system_role_by_user_id(user.id)
            project_roles = await self.role_repository.get_project_roles_by_user_id(user.id)
            system_permissions = await self.permission_repository.get_system_permissions_by_user_id(user.id)
            project_permissions = await self.permission_repository.get_permissions_of_all_projects_by_user_id(user.id)

            # Create token payload with all authorization info
            # Build project permissions dict mapping project_id -> permission list
            project_perms_dict: Dict[str, List[str]] = {}
            for proj_perm in project_permissions:
                project_perms_dict[str(proj_perm.project_name)] = [p.name for p in proj_perm.permissions]

            # Build project roles dict mapping project_name -> role name
            project_roles_dict: Dict[str, str] = {}
            for proj_role in project_roles:
                project_roles_dict[str(proj_role.project_name)] = proj_role.role_name

            token_payload = TokenPayload(
                sub=str(user.id),
                email=user.email,
                name=user.name,
                system_role=system_role.role_name if system_role else "",
                system_permissions=[p.name for p in system_permissions.permissions],
                project_roles=project_roles_dict,
                project_permissions=project_perms_dict
            )

            # Create access token
            access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = self._create_token(token_payload, access_token_expires)

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
                self._public_key,
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
            return cached_token.access_token

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

    async def get_valid_microsoft_token(self, user_id: int) -> Optional[CachedToken]:
        """Get valid Microsoft token"""
        # Try to get from cache first
        token = await self.redis_service.get_cached_token(user_id, TokenType.MICROSOFT)
        if token:
            return token

        # If not in cache, refresh token
        new_access_token = await self.token_refresh_service.refresh_microsoft_token(user_id)
        if not new_access_token:
            log.error("Failed to get valid Microsoft token")
            raise TokenError("Failed to get valid Microsoft token")

        # Cache new token
        await self.redis_service.cache_token(user_id, new_access_token, settings.MICROSOFT_TOKEN_EXPIRATION_TIME, TokenType.MICROSOFT)
        return CachedToken(
            access_token=new_access_token,
            expires_at=datetime.now() + timedelta(seconds=settings.MICROSOFT_TOKEN_EXPIRATION_TIME),
            token_type=TokenType.MICROSOFT
        )

    async def get_valid_jira_token(self, user_id: int) -> Optional[CachedToken]:
        """Get valid Jira token"""
        # Try to get from cache first
        token = await self.redis_service.get_cached_token(user_id, TokenType.JIRA)
        if token:
            return token

        # If not in cache, refresh token
        new_access_token = await self.token_refresh_service.refresh_jira_token(user_id)
        if not new_access_token:
            raise TokenError("Failed to get valid Jira token")

        # Cache new token
        await self.redis_service.cache_token(user_id, new_access_token, settings.JIRA_TOKEN_EXPIRATION_TIME, TokenType.JIRA)

        return CachedToken(
            access_token=new_access_token,
            expires_at=datetime.now() + timedelta(seconds=settings.JIRA_TOKEN_EXPIRATION_TIME),
            token_type=TokenType.JIRA
        )

    def _load_keys(self) -> None:
        """Load private and public keys from PEM files"""
        try:
            private_key_path = Path(settings.JWT_PRIVATE_KEY_PATH)
            public_key_path = Path(settings.JWT_PUBLIC_KEY_PATH)

            with open(private_key_path, 'rb') as private_file:
                self._private_key = private_file.read()

            with open(public_key_path, 'rb') as public_file:
                self._public_key = public_file.read()

        except Exception as e:
            log.error(f"Failed to load JWT keys: {str(e)}")
            raise RuntimeError("Failed to initialize JWT service") from e

    def _create_token(self, payload: TokenPayload, expires_delta: timedelta) -> str:
        """Create JWT token with role and permission claims"""
        expires_at = datetime.now() + expires_delta

        token_payload = {
            **payload.model_dump(),
            "exp": expires_at,
            "iat": datetime.now(),
            'iss': settings.JWT_ISSUER
        }

        return cast(str, jwt.encode(
            token_payload,
            self._private_key,
            algorithm=settings.JWT_ALGORITHM
        ))

    def _decode_token(self, token: str) -> TokenPayload:
        """Decode and verify JWT token"""
        payload = jwt.decode(
            token,
            self._public_key,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return TokenPayload.model_validate(payload)
