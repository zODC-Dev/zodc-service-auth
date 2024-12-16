from typing import Optional

from sqlmodel.ext.asyncio.session import AsyncSession

from src.domain.constants.roles import Roles
from src.domain.entities.auth import MicrosoftIdentity, UserCredentials
from src.domain.entities.user import User as UserEntity
from src.domain.exceptions.user_exceptions import UserCreationError
from src.domain.repositories.auth_repository import IAuthRepository
from src.infrastructure.models.user import User as UserModel
from src.infrastructure.repositories.sqlalchemy_role_repository import SQLAlchemyRoleRepository
from src.infrastructure.repositories.sqlalchemy_user_repository import SQLAlchemyUserRepository
from src.infrastructure.services.bcrypt_service import verify_password


class SQLAlchemyAuthRepository(IAuthRepository):
    def __init__(self, session: AsyncSession, user_repository: SQLAlchemyUserRepository, role_repository: SQLAlchemyRoleRepository):
        self.session = session
        self.user_repository = user_repository
        self.role_repository = role_repository

    async def verify_credentials(
        self,
        credentials: UserCredentials
    ) -> Optional[UserEntity]:
        user = await self.user_repository.get_user_by_email(credentials.email)
        if not user:
            return None

        if not user.password or not verify_password(credentials.password, user.password):
            return None

        return user

    async def create_sso_user(self, microsoft_identity: MicrosoftIdentity) -> UserEntity:
        new_user = UserModel(
            email = microsoft_identity.email,
            name = microsoft_identity.name or microsoft_identity.email,
            is_active = True
        )
        self.session.add(new_user)
        await self.session.commit()
        await self.session.refresh(new_user)

        if new_user.id is None:
            raise UserCreationError("Something went wrong")

        # Assign default role
        await self.role_repository.assign_system_role_to_user(new_user.id, Roles.USER)

        return self._to_domain(new_user)

    async def update_refresh_token(self, user_id: int, refresh_token: str) -> None:
        user = await self.user_repository.get_user_by_id(user_id)
        if user:
            user.microsoft_refresh_token = refresh_token
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
