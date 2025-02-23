from typing import Any, Dict

from src.app.services.project_service import ProjectService
from src.configs.logger import log
from src.domain.constants.nats_events import NATSSubscribeTopic
from src.domain.events.project_events import JiraUsersResponseEvent
from src.domain.services.nats_service import INATSService


class NATSSubscribeService:
    def __init__(
        self,
        nats_service: INATSService,
        project_service: ProjectService
    ):
        self.nats_service = nats_service
        self.project_service = project_service

    async def start_nats_subscribers(self) -> None:
        """Start NATS subscribers"""
        for event_type in NATSSubscribeTopic:
            if event_type == NATSSubscribeTopic.JIRA_USERS_RESPONSE:
                await self.nats_service.subscribe(
                    subject=event_type.value,
                    callback=self.handle_jira_users_response_event
                )

    async def handle_jira_users_response_event(self, subject: str, data: Dict[str, Any]) -> None:
        """Route Jira users found event to project service"""
        try:
            event = JiraUsersResponseEvent.model_validate(data)
            await self.project_service.handle_jira_users_response_event(event)
        except Exception as e:
            log.error(f"Error handling Jira users found event: {str(e)}")
