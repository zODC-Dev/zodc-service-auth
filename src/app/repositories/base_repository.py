from sqlalchemy.ext.asyncio import AsyncSession
from src.configs.database import Base
from src.configs.logger import log
from sqlalchemy.sql import select

class BaseRepository:
    def __init__(self, model: Base):
        self.model = model

    async def create(self, db: AsyncSession, obj_in):
        db_obj = self.model(**obj_in.dict())
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        log.debug(f"Created {self.model.__name__} with id: {db_obj.id}")
        return db_obj

    async def get(self, db: AsyncSession, id: int):
        result = await db.execute(
            select(self.model).filter(self.model.id == id)
        )
        return result.scalar_one_or_none()

    async def get_all(self, db: AsyncSession, skip: int = 0, limit: int = 100):
        result = await db.execute(
            select(self.model).offset(skip).limit(limit)
        )
        return result.scalars().all()

    async def update(self, db: AsyncSession, id: int, obj_in):
        db_obj = await self.get(db, id)
        if db_obj:
            obj_data = obj_in.dict(exclude_unset=True)
            for key, value in obj_data.items():
                setattr(db_obj, key, value)
            await db.commit()
            await db.refresh(db_obj)
        return db_obj

    async def delete(self, db: AsyncSession, id: int):
        db_obj = await self.get(db, id)
        if db_obj:
            await db.delete(db_obj)
            await db.commit()
        return db_obj