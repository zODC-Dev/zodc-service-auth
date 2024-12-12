from typing import Optional

from sqlmodel.ext.asyncio.session import AsyncSession

from src.configs.logger import logger
from src.domain.entities.auth import MicrosoftIdentity, UserCredentials, UserIdentity
from src.domain.repositories.auth_repository import IAuthRepository
from src.infrastructure.models.user import User
from src.infrastructure.repositories.sqlalchemy_user_repository import SQLAlchemyUserRepository
from src.infrastructure.security.password import verify_password


class SQLAlchemyAuthRepository(IAuthRepository):
    def __init__(self, session: AsyncSession, user_repository: SQLAlchemyUserRepository):
        self.session = session
        self.user_repository = user_repository

    async def verify_credentials(
        self,
        credentials: UserCredentials
    ) -> Optional[UserIdentity]:
        user = await self.user_repository.get_user_by_email(credentials.email)
        if not user:
            return None

        if not user.password or not verify_password(credentials.password, user.password):
            return None

        return user

    async def create_sso_user(self, microsoft_identity: MicrosoftIdentity) -> UserIdentity:
        try:
            new_user = User(
                email = microsoft_identity.email,
                full_name = microsoft_identity.name,
                roles = ["user"], # default role for sso user
                permissions = [], # default permission for sso user
                is_active = True
            )
            self.session.add(new_user)
            await self.session.commit()
            await self.session.refresh(new_user)
            return self._to_domain(new_user)
        except Exception as e:
            logger.error(f"error: {str(e)}")

    async def update_refresh_token(self, user_id: int, refresh_token: str) -> None:
        user = await self.user_repository.get_user_by_id(user_id)
        if user:
            user.microsoft_refresh_token = refresh_token
            await self.session.commit()

    def _to_domain(self, user: User) -> UserIdentity:
        return UserIdentity(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            roles=user.roles,
            permissions=user.permissions,
            is_active=user.is_active
        )
