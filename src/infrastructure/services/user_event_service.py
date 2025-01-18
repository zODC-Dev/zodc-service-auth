from typing import Any, Dict

from src.configs.logger import log
from src.domain.constants.user_events import UserEventType
from src.domain.entities.user_event import UserEvent
from src.domain.services.nats_service import INATSService
from src.domain.services.user_event_service import IUserEventService


class UserEventService(IUserEventService):
    def __init__(self, nats_service: INATSService):
        self.nats_service = nats_service

    async def publish_user_event(
        self,
        user_id: int,
        event_type: UserEventType,
        data: Dict[str, Any] = None
    ) -> None:
        try:
            event = UserEvent(
                event_type=event_type,
                user_id=user_id,
                data=data
            )

            await self.nats_service.publish(
                subject=event_type.value,
                message=event.model_dump()
            )

            log.debug(f"Published user event: {event_type.value} for user {user_id}")
        except Exception as e:
            log.error(f"Failed to publish user event: {str(e)}")
            raise
