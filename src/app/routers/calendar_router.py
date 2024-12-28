from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query

from src.app.controllers.calendar_controller import CalendarController
from src.app.dependencies.auth import get_current_user_id
from src.app.dependencies.calendar import get_calendar_controller
from src.app.schemas.responses.calendar import CalendarEventsResponse

router = APIRouter()

@router.get("/", response_model=CalendarEventsResponse)
async def get_calendar_events(
    start_time: Optional[datetime] = Query(None),
    end_time: Optional[datetime] = Query(None),
    page_size: int = Query(50, gt=0, le=100),
    next_link: Optional[str] = Query(None),
    current_user_id: int = Depends(get_current_user_id),
    controller: CalendarController = Depends(get_calendar_controller)
):
    """Get user's calendar events with optional date range and pagination."""
    return await controller.get_calendar_events(
        user_id=current_user_id,
        start_time=start_time,
        end_time=end_time,
        page_size=page_size,
        next_link=next_link
    )
