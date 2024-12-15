from fastapi import Depends
from redis.asyncio import Redis
from sqlmodel.ext.asyncio.session import AsyncSession

from src.app.controllers.calendar_controller import CalendarController
from src.app.services.calendar_service import CalendarService
from src.configs.database import get_db
from src.configs.redis_config import get_redis_client
from src.infrastructure.repositories.microsoft_calendar_repository import MicrosoftCalendarRepository
from src.infrastructure.services.jwt_token_service import JWTTokenService
from src.infrastructure.services.redis_service import RedisService


async def get_redis_service(redis_client: Redis = Depends(get_redis_client)):
    """Dependency for redis repository"""
    return RedisService(redis_client=redis_client)

async def get_token_service(redis_client: RedisService = Depends(get_redis_service)):
    """Dependency for token service"""
    return JWTTokenService(redis_service=redis_client)

async def get_calendar_repository(
    db: AsyncSession = Depends(get_db),
    token_service = Depends(get_token_service)
):
    """Dependency for calendar repository"""
    return MicrosoftCalendarRepository(
        token_service=token_service,
        db_session=db
    )

async def get_calendar_service(
    calendar_repository = Depends(get_calendar_repository)
):
    """Dependency for calendar service"""
    return CalendarService(calendar_repository)

async def get_calendar_controller(
    calendar_service = Depends(get_calendar_service)
):
    """Dependency for calendar controller"""
    return CalendarController(calendar_service)
