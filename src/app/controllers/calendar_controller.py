from datetime import datetime
from typing import Optional

from fastapi import HTTPException

from src.app.schemas.responses.calendar import CalendarEventsResponse
from src.app.services.calendar_service import CalendarService
from src.configs.logger import log
from src.domain.exceptions.calendar_exceptions import CalendarError


class CalendarController:
    def __init__(self, calendar_service: CalendarService):
        self.calendar_service = calendar_service

    async def get_calendar_events(
        self,
        user_id: int,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        page_size: int = 50,
        next_link: Optional[str] = None,
    ) -> CalendarEventsResponse:
        try:
            events_list = await self.calendar_service.get_user_events(
                user_id=user_id,
                start_time=start_time,
                end_time=end_time,
                page_size=page_size,
                next_link=next_link
            )
            return CalendarEventsResponse(events=events_list.events, next_link=events_list.next_link)
        except CalendarError as e:
            raise HTTPException(status_code=500, detail=str(e)) from e
        except Exception as e:
            log.error(f"Calendar controller error: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error") from e
