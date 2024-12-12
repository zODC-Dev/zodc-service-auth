from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession

from .settings import settings

engine = create_async_engine(str(settings.DATABASE_URL), echo=settings.DEBUG)
AsyncSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()


async def get_db():
    """Create a new database session for each request.

    Yields:
        AsyncSession: a new database session
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
