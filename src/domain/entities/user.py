from typing import Optional

from pydantic import BaseModel, EmailStr

from .base import BaseEntity
from .role import Role


class User(BaseEntity):
    id: Optional[int]
    email: EmailStr
    password: Optional[str] = None
    name: Optional[str] = None
    is_active: bool = True
    microsoft_id: Optional[str] = None
    microsoft_token: Optional[str] = None
    microsoft_refresh_token: Optional[str] = None

    # System-wide role
    system_role: Optional[Role]

class UserCreate(BaseModel):
    email: EmailStr
    name: str
    microsoft_refresh_token: Optional[str] = None

class UserUpdate(BaseModel):
    name: Optional[str] = None
    is_active: Optional[bool] = None
    microsoft_refresh_token: Optional[str] = None
    jira_refresh_token: Optional[str] = None
