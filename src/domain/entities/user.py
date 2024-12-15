from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field


class User(BaseModel):
    id: Optional[int]
    email: EmailStr
    password: Optional[str] = None
    full_name: Optional[str] = None
    roles: List[str] = Field(default_factory=lambda: ["user"])
    permissions: List[str] = Field(default_factory=list)
    is_active: bool = True
    created_at: datetime
    microsoft_id: Optional[str] = None
    microsoft_token: Optional[str] = None
    microsoft_refresh_token: Optional[str] = None
