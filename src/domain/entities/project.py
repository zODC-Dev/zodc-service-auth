from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from pydantic import BaseModel, Field

from .base import BaseEntity

if TYPE_CHECKING:
    from .user import User
    from .user_project_role import UserProjectRole


class Project(BaseEntity):
    id: Optional[int] = None
    name: str
    key: str
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    avatar_url: Optional[str] = None

    # Relationships
    users: Optional[List["User"]] = None
    user_project_roles: Optional[List["UserProjectRole"]] = None
    # user_history: Optional[List["UserProjectHistory"]] = None
    # performance_records: Optional[List["UserPerformance"]] = None

    class Config:
        from_attributes = True


class ProjectCreate(BaseModel):
    name: str
    key: str
    description: Optional[str] = None
    avatar_url: Optional[str] = None


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    key: Optional[str] = None
    description: Optional[str] = None
