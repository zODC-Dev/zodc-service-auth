from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from src.domain.entities.user import User


class UserResponse(BaseModel):
    id: int
    email: str
    name: Optional[str]
    system_role: Optional[str] = None
    is_active: bool
    created_at: datetime

    @classmethod
    def from_domain(cls, user: User) -> "UserResponse":
        return cls(
            id=user.id,
            email=user.email,
            name=user.name,
            system_role=user.system_role.name if user.system_role else None,
            is_active=user.is_active,
            created_at=user.created_at
        )
