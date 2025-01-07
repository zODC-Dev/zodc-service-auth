from typing import List, Optional

from pydantic import BaseModel

from .base import BaseEntity


class Permission(BaseEntity):
    name: str
    description: Optional[str] = None
    group: Optional[str] = None


class PermissionCreate(BaseModel):
    name: str
    description: Optional[str] = None


class PermissionVerificationPayload(BaseModel):
    token: str
    user_id: int
    permissions: List[str]
    project_id: Optional[int] = None
    scope: str = "system"  # "system" or "project"


class PermissionVerificationResult(BaseModel):
    allowed: bool
    user_id: int
    permissions: List[str]
    scope: str
    project_id: Optional[int] = None
    error: Optional[str] = None
