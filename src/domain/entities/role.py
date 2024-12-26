from typing import TYPE_CHECKING, List, Optional

from pydantic import BaseModel, Field

from .base import BaseEntity

if TYPE_CHECKING:
    from .permission import Permission
    from .user import User
    from .user_project_role import UserProjectRole


class Role(BaseEntity):
    name: str
    description: Optional[str] = None
    is_system_role: bool = False
    is_active: bool = True
    permissions: List["Permission"] = []
    user_project_roles: List["UserProjectRole"] = []
    users: List["User"] = []


class RoleCreate(BaseModel):
    name: str
    description: Optional[str] = None
    is_system_role: bool = False
    is_active: bool = True
    permission_names: List[str] = Field(default_factory=list)


class RoleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    permission_names: Optional[List[str]] = None
    is_system_role: Optional[bool] = None
    is_active: Optional[bool] = None
