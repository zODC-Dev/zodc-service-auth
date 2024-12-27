from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, HttpUrl


class CalendarEventResponse(BaseModel):
    id: str
    title: str
    start_time: datetime
    end_time: datetime
    # Add other necessary fields


class CalendarEventsResponse(BaseModel):
    events: List[CalendarEventResponse]
    next_link: Optional[HttpUrl] = None
