from datetime import datetime
from fastapi import HTTPException
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from src.configs.logger import logger
from src.app.exceptions.calendar import CalendarException
from src.app.services.graph_service import graph_service, GraphService

class CalendarController:
    def __init__(self, graph_service: GraphService):
        self.graph_service = graph_service

    async def get_calendar_events(
        self,
        user_id: int,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        page_size: int = 50,
        next_link: Optional[str] = None,
        db: AsyncSession = None
    ):
        try:
            logger.info(f"Fetching calendar events for user {user_id}")
            return await self.graph_service.get_calendar_events(
                user_id=user_id,
                start_time=start_time,
                end_time=end_time,
                page_size=page_size,
                next_link=next_link,
                db=db
            )
        except Exception as e:
            logger.error(f"Calendar controller error: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to fetch calendar events")

calendar_controller = CalendarController(graph_service)