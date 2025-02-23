from abc import ABC, abstractmethod
from typing import Any, Dict

from src.domain.constants.nats_events import NATSPublishTopic


class IUserEventService(ABC):
    @abstractmethod
    async def publish_user_event(
        self,
        user_id: int,
        event_type: NATSPublishTopic,
        data: Dict[str, Any] = None
    ) -> None:
        """Publish user event to message broker"""
        pass
