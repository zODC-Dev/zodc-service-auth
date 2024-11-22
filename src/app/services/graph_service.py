from aiohttp import ClientSession
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from msgraph import GraphServiceClient
from msgraph.generated.users.item.calendars.calendars_request_builder import CalendarsRequestBuilder
from azure.identity import AuthorizationCodeCredential, ClientSecretCredential

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
       
        logger.info(f"Graph client: {self.graph_client}")
        query_param = CalendarsRequestBuilder.CalendarsRequestBuilderGetQueryParameters(
            select=["id", "subject", "organizer", "attendees", "start", "end", "isOnlineMeeting", "onlineMeeting"],
        )

        request_config = CalendarsRequestBuilder.CalendarsRequestBuilderGetRequestConfiguration(
            query_parameters=query_param
        )

        calendars = await self.graph_client.me.calendars.get(request_configuration=request_config)
        return {
            "events": [self._parse_event(event) for event in calendars],
        }

    def _parse_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Microsoft Graph event into our schema"""
        return {
            "id": event.get("id"),
            "subject": event.get("subject"),
            "start": datetime.fromisoformat(event["start"]["dateTime"].replace('Z', '')),
            "end": datetime.fromisoformat(event["end"]["dateTime"].replace('Z', '')),
            "organizer": {
                "email": event.get("organizer", {}).get("emailAddress", {}).get("address"),
                "name": event.get("organizer", {}).get("emailAddress", {}).get("name")
            },
            "attendees": [
                {
                    "email": attendee.get("emailAddress", {}).get("address"),
                    "name": attendee.get("emailAddress", {}).get("name"),
                    "response_status": attendee.get("status", {}).get("response")
                }
                for attendee in event.get("attendees", [])
            ],
            "is_online_meeting": event.get("isOnlineMeeting", False),
            "online_meeting_url": event.get("onlineMeeting", {}).get("joinUrl")
        }

graph_service = GraphService(token_service)