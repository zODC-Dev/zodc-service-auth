from typing import TYPE_CHECKING, List, Optional

from pydantic import BaseModel

from .base import BaseEntity

if TYPE_CHECKING:
    from .user_project_role import UserProjectRole


class Project(BaseEntity):
    name: str
    key: str
    description: Optional[str] = None
    user_project_roles: List["UserProjectRole"] = []

    class Config:
        from_attributes = True


class ProjectCreate(BaseModel):
    name: str
    key: str
    description: Optional[str] = None


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    key: Optional[str] = None
    description: Optional[str] = None
