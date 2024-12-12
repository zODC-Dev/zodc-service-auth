from typing import Optional

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.configs.logger import logger
from src.domain.repositories.user_repository import IUserRepository
from src.infrastructure.models.user import User, UserCreate, UserUpdate


class SQLAlchemyUserRepository(IUserRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        result = await self.session.exec(
            select(User).where(User.id == user_id)
        )
        return result.first()

    async def get_user_by_email(self, email: str) -> Optional[User]:
        try:
            result = await self.session.exec(
                select(User).where(User.email == email)
            )
            value = result.first()
            logger.info(f"value: {value}")
            return value
        except Exception as e:
            logger.error(f"{str(e)}")
            return None

    async def create_user(self, user_data: UserCreate) -> User:
        user = User.model_validate(user_data)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def update_user(self, user_id: int, user_data: UserUpdate) -> Optional[User]:
        user = await self.get_user_by_id(user_id)
        if not user:
            return None

        user_data_dict = user_data.model_dump(exclude_unset=True)
        for key, value in user_data_dict.items():
            setattr(user, key, value)

        await self.session.commit()
        await self.session.refresh(user)
        return user
