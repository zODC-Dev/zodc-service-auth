from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from src.domain.entities.user import User


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: Optional[str]
    roles: List[str]
    permissions: List[str]
    is_active: bool
    created_at: datetime

    @classmethod
    def from_domain(cls, user: User) -> "UserResponse":
        return cls(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            roles=user.roles,
            permissions=user.permissions,
            is_active=user.is_active,
            created_at=user.created_at
        )
