from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from pydantic import BaseModel, Field

from .base import BaseEntity

# Use TYPE_CHECKING for circular imports
if TYPE_CHECKING:
    from .project import Project
    from .role import Role
    from .user import User


class UserProjectRole(BaseEntity):
    user_id: int
    project_id: int
    role_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    # Use Optional for relationships to avoid initialization issues
    user: Optional["User"] = None
    project: Optional["Project"] = None
    role: Optional["Role"] = None
    roles: List["Role"] = Field(default_factory=list)

    class Config:
        from_attributes = True


class UserProjectRoleCreate(BaseModel):
    user_id: int
    role_id: int


class UserProjectRoleUpdate(BaseModel):
    role_id: int
