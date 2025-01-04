from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, HttpUrl

from src.domain.entities.calendar import CalendarEvent, CalendarEventsList


class CalendarEventResponse(BaseModel):
    id: str
    subject: str
    start_time: datetime
    end_time: datetime
    organizer_email: EmailStr
    is_online_meeting: bool
    online_meeting_url: Optional[HttpUrl] = None
    attendees: List[EmailStr] = []

    @classmethod
    def from_domain(cls, event: CalendarEvent) -> "CalendarEventResponse":
        return cls(
            id=event.id,
            subject=event.subject,
            start_time=event.start_time,
            end_time=event.end_time,
            organizer_email=event.organizer_email,
            is_online_meeting=event.is_online_meeting,
            online_meeting_url=event.online_meeting_url,
            attendees=event.attendees
        )


class CalendarEventsResponse(BaseModel):
    events: List[CalendarEventResponse]
    next_link: Optional[HttpUrl] = None

    @classmethod
    def from_domain(cls, events_list: CalendarEventsList) -> "CalendarEventsResponse":
        return cls(
            events=[CalendarEventResponse.from_domain(
                event) for event in events_list.events],
            next_link=events_list.next_link
        )
