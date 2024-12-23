from typing import List, Optional

from pydantic import BaseModel, Field

from .base import BaseEntity
from .permission import Permission


class Role(BaseEntity):
    name: str
    description: Optional[str] = None
    is_system_role: bool = False
    is_active: bool = True
    permissions: List[Permission] = []


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
