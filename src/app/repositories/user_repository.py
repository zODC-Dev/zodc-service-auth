from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from ..models.user import User
from ..schemas.user import CreateUserPayload
from src.utils.brcypt_util import BcryptUtil
from sqlalchemy.sql.expression import select

class UserRepository:
    async def get_user_by_email(self, email: str, db: AsyncSession) -> Optional[User]:
        result = await db.execute(select(User).filter(User.email == email))
        return result.scalar_one_or_none()

    async def create_user(self, payload: CreateUserPayload,  db: AsyncSession) -> User:
        # check if user already exists
        user = await UserRepository.get_user_by_email(payload.email, db)
        if user:
            raise Exception("User already exists")

        # create user
        hashed_password = BcryptUtil.hash_password(payload.password)
        user = User(email=payload.email, full_name=payload.full_name, password=hashed_password)
        db.add(user)
        await db.commit()
        return user

user_repository = UserRepository()