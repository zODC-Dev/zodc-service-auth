from typing import Optional

from pydantic import BaseModel

from .base import BaseEntity


class Permission(BaseEntity):
    name: str
    description: Optional[str] = None

class PermissionCreate(BaseModel):
    name: str
    description: Optional[str] = None
