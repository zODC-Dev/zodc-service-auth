from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from pydantic import BaseModel, EmailStr, Field

from .base import BaseEntity

if TYPE_CHECKING:
    from .role import Role
    from .user_project_role import UserProjectRole


class User(BaseEntity):
    id: Optional[int] = None
    email: EmailStr
    password: Optional[str] = None
    name: Optional[str] = None
    is_active: bool = True
    microsoft_id: Optional[str] = None
    microsoft_token: Optional[str] = None
    microsoft_refresh_token: Optional[str] = None
    user_project_roles: Optional[List["UserProjectRole"]] = []
    # System-wide role
    system_role: Optional["Role"] = None
    jira_token: Optional[str] = None
    jira_refresh_token: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)

    # Microsoft tokens
    microsoft_access_token: Optional[str] = None
    microsoft_token_expires_at: Optional[datetime] = None

    # Jira tokens
    jira_access_token: Optional[str] = None
    jira_token_expires_at: Optional[datetime] = None


class UserCreate(BaseModel):
    email: EmailStr
    name: str
    microsoft_refresh_token: Optional[str] = None


class UserUpdate(BaseModel):
    name: Optional[str] = None
    is_active: Optional[bool] = None
    microsoft_refresh_token: Optional[str] = None
    jira_refresh_token: Optional[str] = None
