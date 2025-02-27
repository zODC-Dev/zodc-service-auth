from typing import TYPE_CHECKING, List, Optional

from pydantic import BaseModel, Field

from .base import BaseEntity

if TYPE_CHECKING:
    from .permission import Permission
    from .user_project_role import UserProjectRole


class Role(BaseEntity):
    name: str
    description: Optional[str] = None
    is_system_role: bool = False
    is_active: bool = True
    permissions: Optional[List["Permission"]] = []
    user_project_roles: Optional[List["UserProjectRole"]] = []
    # users: Optional[List["User"]] = []


class RoleCreate(BaseModel):
    name: str
    description: Optional[str] = None
    is_system_role: bool = False
    is_active: bool = True
    permissions: List[int] = Field(default_factory=list)  # permission ids


class RoleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    permission_names: Optional[List[str]] = None
    is_system_role: Optional[bool] = None
    is_active: Optional[bool] = None
