from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class Attendee(BaseModel):
    email: str
    name: Optional[str]
    response_status: Optional[str] = None


class CalendarEvent(BaseModel):
    id: str
    subject: str
    start: datetime
    end: datetime
    organizer: Optional[Attendee]
    attendees: List[Attendee] = []
    is_online_meeting: bool = False
    online_meeting_url: Optional[str]


class CalendarEventsResponse(BaseModel):
    events: List[CalendarEvent]
    next_link: Optional[str] = None
