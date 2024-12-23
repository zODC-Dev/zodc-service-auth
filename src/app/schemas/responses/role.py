from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from src.domain.entities.role import Role


class RoleResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    is_system_role: bool
    is_active: bool
    permission_names: List[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    @classmethod
    def from_domain(cls, role: Role) -> 'RoleResponse':
        return cls(
            id=role.id,
            name=role.name,
            description=role.description,
            is_system_role=role.is_system_role,
            is_active=role.is_active,
            permission_names=[p.name for p in role.permissions],
            created_at=role.created_at,
            updated_at=role.updated_at
        )
