from datetime import datetime
from typing import Optional

from src.configs.logger import logger
from src.domain.entities.calendar import CalendarEventsList
from src.domain.exceptions.calendar_exceptions import CalendarError
from src.domain.repositories.calendar_repository import ICalendarRepository


class CalendarService:
    def __init__(self, calendar_repository: ICalendarRepository):
        self.calendar_repository = calendar_repository

    async def get_user_events(
        self,
        user_id: int,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        page_size: int = 50,
        next_link: Optional[str] = None
    ) -> CalendarEventsList:
        try:
            return await self.calendar_repository.get_user_events(
                user_id=user_id,
                start_time=start_time,
                end_time=end_time,
                page_size=page_size,
                next_link=next_link
            )
        except Exception as e:
            logger.error(f"Error getting calendar events for user {user_id}: {str(e)}")
            raise CalendarError("Failed to fetch calendar events") from e
