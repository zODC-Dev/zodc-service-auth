from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from pydantic import BaseModel, Field

from .base import BaseEntity

if TYPE_CHECKING:
    from .project import Project
    from .user import User


class UserProjectHistory(BaseEntity):
    id: Optional[int] = None
    user_id: int
    project_id: int
    data: Dict[str, Any]
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None

    # Relationships
    user: Optional["User"] = None
    project: Optional["Project"] = None


class UserProjectHistoryCreate(BaseModel):
    user_id: int
    project_id: int
    position: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    description: Optional[str] = None
    technologies: Optional[List[str]] = None


class UserProjectHistoryUpdate(BaseModel):
    position: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    description: Optional[str] = None
    technologies: Optional[List[str]] = None
