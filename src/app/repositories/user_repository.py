from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from ..models.user import User
from ..schemas.user import CreateUserPayload, CreateUserPayloadSSO
from src.utils.brcypt_util import BcryptUtil
from sqlalchemy.sql.expression import select

class UserRepository:
    async def get_user_by_email(self, email: str, db: AsyncSession) -> Optional[User]:
        result = await db.execute(select(User).filter(User.email == email))
        return result.scalar_one_or_none()

    async def get_user_by_id(self, id: str, db: AsyncSession) -> Optional[User]:
        result = await db.execute(select(User).filter(User.id == id))
        return result.scalar_one_or_none()

    async def create_user(self, payload: CreateUserPayload,  db: AsyncSession) -> User:
        # check if user already exists
        user = await self.get_user_by_email(email=payload.email, db=db)
        if user:
            raise Exception("User already exists")

        # create user
        hashed_password = BcryptUtil.hash_password(payload.password)
        user = User(email=payload.email, full_name=payload.full_name, password=hashed_password)
        db.add(user)
        await db.commit()
        return user
    
    async def create_user_by_sso(self, payload: CreateUserPayloadSSO, db: AsyncSession) -> User:
        # check if user already exists
        user = await self.get_user_by_email(email=payload.email, db=db)
        if user:
            raise Exception("User already exists")

        # create user
        user = User(email=payload.email, full_name=payload.full_name, microsoft_id=payload.microsoft_id)
        db.add(user)
        await db.commit()
        return user

    async def update_refresh_token(self, user_id: str, refresh_token: str, db: AsyncSession):
        # get user
        user = await self.get_user_by_id(id=user_id, db=db)
        if user:
            user.microsoft_refresh_token = refresh_token
            await db.commit()
        return user

user_repository = UserRepository()