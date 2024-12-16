from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from .base import BaseEntity
from .project import Project
from .role import Role
from .user import User


class UserProjectRole(BaseEntity):
    user_id: int
    project_id: int
    role_id: int
    assigned_at: datetime
    updated_at: Optional[datetime] = None

    # Relationships
    user: Optional[User] = None
    project: Optional[Project] = None
    role: Optional[Role] = None

class UserProjectRoleCreate(BaseModel):
    user_id: int
    role_id: int

class UserProjectRoleUpdate(BaseModel):
    role_id: int
