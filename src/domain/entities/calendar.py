from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, HttpUrl


class CalendarEvent(BaseModel):
    id: str
    subject: str
    start_time: datetime
    end_time: datetime
    organizer_email: EmailStr
    is_online_meeting: bool
    online_meeting_url: Optional[HttpUrl] = None
    attendees: List[EmailStr] = []

class CalendarEventsList(BaseModel):
    events: List[CalendarEvent]
    next_link: Optional[HttpUrl] = None
