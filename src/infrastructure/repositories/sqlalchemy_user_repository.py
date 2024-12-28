from typing import Optional

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.configs.logger import log
from src.domain.entities.user import User as UserEntity
from src.domain.repositories.user_repository import IUserRepository
from src.infrastructure.models.user import User as UserModel, UserCreate


class SQLAlchemyUserRepository(IUserRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_by_id(self, user_id: int) -> Optional[UserEntity]:
        result = await self.session.exec(
            select(UserModel).where(UserModel.id == user_id)
        )
        user = result.first()
        return self._to_domain(user) if user else None

    async def get_user_by_email(self, email: str) -> Optional[UserEntity]:
        try:
            result = await self.session.exec(
                select(UserModel).where(UserModel.email == email)
            )
            user = result.first()
            return self._to_domain(user) if user else None
        except Exception as e:
            log.error(f"{str(e)}")
            return None

    async def create_user(self, user_data: UserCreate) -> UserEntity:
        user = UserModel.model_validate(user_data)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return self._to_domain(user)

    def _to_domain(self, db_user: UserModel) -> UserEntity:
        """Convert DB model to domain entity"""
        return UserEntity(
            id=db_user.id,
            email=db_user.email,
            name=db_user.name,
            is_active=db_user.is_active,
            created_at=db_user.created_at,
            microsoft_id=db_user.microsoft_id,
            microsoft_refresh_token=db_user.microsoft_refresh_token,
            microsoft_token=db_user.microsoft_token,
            system_role=db_user.system_role,
        )
