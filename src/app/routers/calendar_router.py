from fastapi import APIRouter, Depends, Query
from datetime import datetime
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from src.configs.database import get_db
from src.app.controllers.calendar_controller import calendar_controller
from src.app.middlewares.auth import get_current_user
from src.app.schemas.calendar import CalendarEventsResponse

router = APIRouter()

@router.get("/", response_model=CalendarEventsResponse)
async def get_calendar_events(
    start_time: Optional[datetime] = Query(None),
    end_time: Optional[datetime] = Query(None),
    page_size: int = Query(50, gt=0, le=100),
    next_link: Optional[str] = Query(None),
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user's calendar events with optional date range and pagination.
    If no date range is specified, returns events for the next 7 days.
    """
    return await calendar_controller.get_calendar_events(
        user_id=current_user.id,
        start_time=start_time,
        end_time=end_time,
        page_size=page_size,
        next_link=next_link,
        db=db
    )