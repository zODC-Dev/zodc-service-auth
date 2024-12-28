from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from src.app.controllers.calendar_controller import CalendarController
from src.app.services.calendar_service import CalendarService
from src.configs.database import get_db
from src.infrastructure.repositories.microsoft_calendar_repository import MicrosoftCalendarRepository

from .common import get_token_service


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
