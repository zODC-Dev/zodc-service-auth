from typing import List, Optional

from pydantic import BaseModel, HttpUrl

from src.domain.entities.calendar import CalendarEvent


class CalendarEventsResponse(BaseModel):
    events: List[CalendarEvent]
    next_link: Optional[HttpUrl] = None
