from datetime import datetime
from typing import Any, Dict, Optional

from httpx import AsyncClient
from sqlmodel.ext.asyncio.session import AsyncSession

from src.configs.logger import logger
from src.domain.entities.calendar import CalendarEvent, CalendarEventsList
from src.domain.exceptions.calendar_exceptions import CalendarError
from src.domain.repositories.calendar_repository import ICalendarRepository
from src.infrastructure.services.jwt_token_service import JWTTokenService


class MicrosoftCalendarRepository(ICalendarRepository):
    BASE_URL = "https://graph.microsoft.com/v1.0"

    def __init__(self, token_service: JWTTokenService, db_session: AsyncSession):
        self.token_service = token_service
        self.db_session = db_session

    async def get_user_events(
        self,
        user_id: int,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        page_size: int = 50,
        next_link: Optional[str] = None
    ) -> CalendarEventsList:
        try:
            # Get Microsoft token
            microsoft_access_token = await self.token_service.get_microsoft_token(
                user_id,
                self.db_session
            )

            # Build URL and params
            url = next_link or f"{self.BASE_URL}/me/calendar/events"
            params = self._build_query_params(
                start_time,
                end_time,
                page_size
            )

            # Call Microsoft Graph API
            async with AsyncClient() as client:
                response = await client.get(
                    url,
                    params=params,
                    headers=self._get_headers(microsoft_access_token)
                )

                if response.status_code == 200:
                    data = response.json()
                    return self._parse_response(data)
                else:
                    logger.error(
                        f"Microsoft Graph API error: {response.status_code} - {response.text}"
                    )
                    raise CalendarError("Failed to fetch calendar events")

        except Exception as e:
            logger.error(f"Calendar repository error: {str(e)}")
            raise CalendarError("Failed to fetch calendar events") from e

    def _build_query_params(
        self,
        start_time: Optional[datetime],
        end_time: Optional[datetime],
        page_size: int
    ) -> Dict[str, Any]:
        """Build query parameters for Microsoft Graph API"""
        params = {
            "$top": page_size,
            "$orderby": "start/dateTime",
            "$select": "id,subject,organizer,attendees,start,end,isOnlineMeeting,onlineMeeting"
        }

        if start_time and end_time:
            params["$filter"] = (
                f"start/dateTime ge '{start_time.isoformat()}Z' and "
                f"end/dateTime le '{end_time.isoformat()}Z'"
            )

        return params

    def _get_headers(self, access_token: str) -> Dict[str, str]:
        """Get headers for Microsoft Graph API"""
        return {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json"
        }

    def _parse_event(self, event: Dict[str, Any]) -> CalendarEvent:
        online_meeting = event.get("onlineMeeting")
        online_meeting_url = online_meeting.get("joinUrl") if online_meeting else None
        return CalendarEvent(
            id=event["id"],
            subject=event["subject"],
            start_time=datetime.fromisoformat(event["start"]["dateTime"].replace('Z', '')),
            end_time=datetime.fromisoformat(event["end"]["dateTime"].replace('Z', '')),
            organizer_email=event["organizer"]["emailAddress"]["address"],
            is_online_meeting=event.get("isOnlineMeeting", False),
            online_meeting_url=online_meeting_url,
            attendees=[
                attendee["emailAddress"]["address"]
                for attendee in event.get("attendees", [])
            ]
        )

    def _parse_response(self, data: Dict[str, Any]) -> CalendarEventsList:
        """Parse Microsoft Graph API response to domain entity"""
        events = [self._parse_event(event) for event in data.get("value", [])]

        return CalendarEventsList(
            events=events,
            next_link=data.get("@odata.nextLink")
        )
