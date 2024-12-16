from typing import List, Optional

from pydantic import BaseModel

from .base import BaseEntity
from .user_project_role import UserProjectRole


class Project(BaseEntity):
    key: str
    description: Optional[str] = None
    user_roles: List[UserProjectRole] = []

class ProjectCreate(BaseModel):
    key: str
    description: Optional[str] = None

class ProjectUpdate(BaseModel):
    description: Optional[str] = None
