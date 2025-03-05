from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlmodel.ext.asyncio.session import AsyncSession

from src.configs.logger import log
from src.domain.constants.auth import TokenType
from src.domain.constants.roles import SystemRoles
from src.domain.entities.auth import MicrosoftIdentity, UserCredentials
from src.domain.entities.user import User as UserEntity
from src.domain.exceptions.user_exceptions import UserCreationError
from src.domain.repositories.auth_repository import IAuthRepository
from src.domain.repositories.refresh_token_repository import IRefreshTokenRepository
from src.domain.repositories.role_repository import IRoleRepository
from src.domain.repositories.user_repository import IUserRepository
from src.infrastructure.models.refresh_token import RefreshToken as RefreshTokenModel
from src.infrastructure.models.user import User as UserModel
from src.infrastructure.services.bcrypt_service import BcryptService


class SQLAlchemyAuthRepository(IAuthRepository):
    def __init__(self, session: AsyncSession, user_repository: IUserRepository, role_repository: IRoleRepository, refresh_token_repository: IRefreshTokenRepository):
        self.session = session
        self.user_repository = user_repository
        self.role_repository = role_repository
        self.refresh_token_repository = refresh_token_repository

    async def verify_credentials(
        self,
        credentials: UserCredentials
    ) -> Optional[UserEntity]:
        try:
            user = await self.user_repository.get_user_with_password_by_email(credentials.email)
            if not user:
                return None

            if not user.password or not BcryptService.verify_password(credentials.password, user.password):
                return None
            return user
        except Exception as e:
            log.error(f"{str(e)}")
            return None

    async def create_sso_user(self, microsoft_identity: MicrosoftIdentity) -> UserEntity:
        new_user = UserModel(
            email=microsoft_identity.email,
            name=microsoft_identity.name or microsoft_identity.email,
            is_active=True,
            is_system_user=True,  # Users who log in via Microsoft are system users
        )
        self.session.add(new_user)
        await self.session.commit()
        await self.session.refresh(new_user)

        if new_user.id is None:
            raise UserCreationError("Something went wrong")

        # Assign default role
        await self.role_repository.assign_system_role_to_user(new_user.id, SystemRoles.USER)

        return self._to_domain(new_user)

    async def update_refresh_token(self, user_id: int, refresh_token: str, token_type: TokenType) -> None:
        user = await self.user_repository.get_user_by_id(user_id)
        if user and user.id:
            existing_refresh_token = await self.refresh_token_repository.get_by_user_id_and_type(user.id, token_type)
            if existing_refresh_token:
                existing_refresh_token.is_revoked = True

            new_refresh_token = RefreshTokenModel(
                user_id=user.id,
                token=refresh_token,
                token_type=token_type,
                expires_at=(datetime.now() + timedelta(days=30)).astimezone(timezone.utc)
            )
            await self.session.add(new_refresh_token)  # type: ignore
            await self.session.commit()

    def _to_domain(self, user: UserModel) -> UserEntity:
        return UserEntity(
            id=user.id,
            email=user.email,
            name=user.name,
            system_role=user.system_role,
            is_active=user.is_active,
            created_at=user.created_at,
        )
