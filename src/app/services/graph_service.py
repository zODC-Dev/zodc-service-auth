from aiohttp import ClientSession
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from msgraph import GraphServiceClient
from msgraph.generated.users.item.calendars.calendars_request_builder import CalendarsRequestBuilder
from azure.identity import AuthorizationCodeCredential, ClientSecretCredential
from httpx import AsyncClient

from src.configs.settings import settings
from src.configs.logger import logger
from src.app.exceptions.calendar import CalendarException
from src.app.services.token_service import token_service, TokenService

class GraphService:
    BASE_URL = "https://graph.microsoft.com/v1.0"
    graph_client: GraphServiceClient

    
    def __init__(self, token_service: TokenService):
        self.token_service = token_service
        self.graph_client = None

    async def initialize(self, credential: AuthorizationCodeCredential):
        """Initialize Graph client"""

        if self.graph_client is None:
            logger.info("Initializing Graph client")
            # scopes = ["https://graph.microsoft.com/.default"]
            scopes = [
                # "https://graph.microsoft.com/.default",
                "https://graph.microsoft.com/Calendars.Read",
                "https://graph.microsoft.com/Calendars.ReadWrite",
                "https://graph.microsoft.com/User.Read"
            ]
            # self.graph_client = GraphServiceClient(credential, settings.AZURE_AD_SCOPES)
            self.graph_client = GraphServiceClient(credentials=credential, scopes=scopes)
            # self.graph_client = GraphServiceClient(credentials=credential)
            logger.info(self.graph_client)

    async def get_calendar_events(
        self,
        user_id: int,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        page_size: int = 50,
        next_link: Optional[str] = None,
        db: AsyncSession = None
    ) -> Dict[str, Any]:
        try:
            # Get Microsoft token from Redis
            access_token = await self.token_service.get_microsoft_token(user_id, db)
            
            # Build URL and params
            url = next_link or f"{self.BASE_URL}/me/calendar/events"
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

            # Call Microsoft Graph API
            async with AsyncClient() as client:
                logger.info(f"Calling Graph API for user {user_id}")
                response = await client.get(
                    url,
                    params=params,
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Accept": "application/json"
                    }
                )

                if response.status_code == 200:
                    data = response.json()
                    logger.info(f"Graph API response: {data}")
                    events = [self._parse_event(event) for event in data["value"]]
                    logger.info(f"Events: {events}")
                    return {
                        "events": events,
                        "next_link": data.get("@odata.nextLink")
                    }
                else:
                    raise CalendarException.API_ERROR

        except Exception as e:
            logger.error(f"Failed to fetch calendar events: {str(e)}")
            raise CalendarException.FETCH_ERROR

    async def get_user_info(self) -> Dict[str, Any]:
        """Get user info from Microsoft Graph"""
        logger.info("Getting user info")
        user = await self.graph_client.me.get()
        return {
            "email": user.get("mail"),
            "name": user.get("displayName")
        }

    def _parse_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Microsoft Graph event response"""
        if not event:
            logger.error("Empty event received")
            return None

        try:
            # Basic event data
            parsed_event = {
                "id": event.get("id", ""),
                "subject": event.get("subject", "No subject"),
                "start": datetime.fromisoformat(
                    event.get("start", {}).get("dateTime", "").split('.')[0]
                ) if event.get("start") else None,
                "end": datetime.fromisoformat(
                    event.get("end", {}).get("dateTime", "").split('.')[0]
                ) if event.get("end") else None,
            }

            # Organizer information
            organizer_data = event.get("organizer", {}).get("emailAddress", {})
            parsed_event["organizer"] = {
                "email": organizer_data.get("address", ""),
                "name": organizer_data.get("name", "")
            }

            # Attendees information
            parsed_event["attendees"] = [
                {
                    "email": attendee.get("emailAddress", {}).get("address", ""),
                    "name": attendee.get("emailAddress", {}).get("name", ""),
                    "response_status": attendee.get("status", {}).get("response", "none")
                }
                for attendee in event.get("attendees", [])
            ]

            # Online meeting information - handle None case
            parsed_event["is_online_meeting"] = event.get("isOnlineMeeting", False)
            online_meeting = event.get("onlineMeeting", {})
            parsed_event["online_meeting_url"] = online_meeting.get("joinUrl", "") if online_meeting else ""

            return parsed_event

        except Exception as e:
            logger.error(f"Error parsing event: {str(e)}")
            logger.error(f"Event data: {event}")
            return None

graph_service = GraphService(token_service)