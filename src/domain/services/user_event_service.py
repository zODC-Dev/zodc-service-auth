from abc import ABC, abstractmethod
from typing import Any, Dict

from src.domain.constants.user_events import UserEventType


class IUserEventService(ABC):
    @abstractmethod
    async def publish_user_event(
        self,
        user_id: int,
        event_type: UserEventType,
        data: Dict[str, Any] = None
    ) -> None:
        """Publish user event to message broker"""
        pass
