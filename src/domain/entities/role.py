
from typing import List, Optional

from pydantic import BaseModel

from .base import BaseEntity
from .permission import Permission


class Role(BaseEntity):
    name: str
    description: Optional[str] = None
    permissions: List[Permission] = []

class RoleCreate(BaseModel):
    name: str
    description: Optional[str] = None
    permission_ids: List[int] = []

class RoleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    permission_ids: Optional[List[int]] = None
