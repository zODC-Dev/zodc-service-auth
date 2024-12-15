from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional

from src.domain.entities.calendar import CalendarEventsList


class ICalendarRepository(ABC):
    @abstractmethod
    async def get_user_events(
        self,
        user_id: int,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        page_size: int = 50,
        next_link: Optional[str] = None
    ) -> CalendarEventsList:
        """Get user's calendar events"""
        pass
