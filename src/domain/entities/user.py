from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from pydantic import BaseModel, EmailStr, Field

from .base import BaseEntity

if TYPE_CHECKING:
    from .role import Role
    from .user_project_role import UserProjectRole


class User(BaseEntity):
    id: Optional[int] = None
    email: EmailStr
    name: Optional[str] = None
    is_active: bool = True
    microsoft_id: Optional[str] = None
    jira_account_id: Optional[str] = None
    is_jira_linked: bool = False
    is_system_user: bool = True  # Default to True for users who log in
    user_project_roles: Optional[List["UserProjectRole"]] = []
    # System-wide role
    system_role: Optional["Role"] = None
    jira_token: Optional[str] = None
    jira_refresh_token: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    avatar_url: Optional[str] = None  # User's avatar URL from Jira
    # Profile data fields
    profile_data: Optional[Dict[str, Any]] = None
    job_title: Optional[str] = None
    location: Optional[str] = None
    phone_number: Optional[str] = None
    joined_date: Optional[datetime] = None


class UserCreate(BaseModel):
    email: EmailStr
    name: str
    is_active: bool = True
    jira_account_id: Optional[str] = None
    is_jira_linked: bool = False
    is_system_user: bool = True  # Default to True for users who log in
    avatar_url: Optional[str] = None  # User's avatar URL from Jira
    profile_data: Optional[Dict[str, Any]] = None
    job_title: Optional[str] = None
    location: Optional[str] = None
    phone_number: Optional[str] = None
    joined_date: Optional[datetime] = None


class UserUpdate(BaseModel):
    name: Optional[str] = None
    is_active: Optional[bool] = None
    jira_account_id: Optional[str] = None
    is_jira_linked: Optional[bool] = None
    avatar_url: Optional[str] = None  # User's avatar URL from Jira
    is_system_user: Optional[bool] = None
    updated_at: Optional[datetime] = None
    profile_data: Optional[Dict[str, Any]] = None
    job_title: Optional[str] = None
    location: Optional[str] = None
    phone_number: Optional[str] = None
    joined_date: Optional[datetime] = None


class UserProfileUpdate(BaseModel):
    job_title: Optional[str] = None
    location: Optional[str] = None
    phone_number: Optional[str] = None
    joined_date: Optional[datetime] = None
    profile_data: Optional[Dict[str, Any]] = None


class UserWithPassword(User):
    password: str
