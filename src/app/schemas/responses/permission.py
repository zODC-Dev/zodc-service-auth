from typing import Optional

from pydantic import BaseModel

from src.domain.entities.permission import Permission


class PermissionResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None

    @classmethod
    def from_domain(cls, permission: Permission):
        return cls(
            id=permission.id,
            name=permission.name,
            description=permission.description
        )
