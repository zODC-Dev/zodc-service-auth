from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, field_serializer

from src.domain.constants.user_events import UserEventType


class UserEvent(BaseModel):
    event_type: UserEventType
    user_id: int
    timestamp: datetime = datetime.now()
    data: Optional[Dict[str, Any]] = None

    @field_serializer('event_type')
    def serialize_event_type(self, event_type: UserEventType) -> str:
        """Serialize UserEventType enum to string"""
        return event_type.value

    @field_serializer('timestamp')
    def serialize_timestamp(self, timestamp: datetime) -> float:
        """Serialize datetime to timestamp"""
        return timestamp.timestamp()
