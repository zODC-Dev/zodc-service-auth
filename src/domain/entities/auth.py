from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field


class UserCredentials(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)

class AuthToken(BaseModel):
    access_token: str
    expires_at: datetime
    token_type: str = "bearer"
    refresh_token: Optional[str] = None

class UserIdentity(BaseModel):
    id: Optional[int]
    email: EmailStr
    full_name: Optional[str]
    roles: List[str] = Field(default_factory=lambda: ["user"])
    permissions: List[str] = Field(default_factory=list)
    is_active: bool = True

class MicrosoftIdentity(BaseModel):
    email: str
    name: Optional[str]
    access_token: str
    expires_in: int
    refresh_token: Optional[str]
    scope: str

class SSOCredentials(BaseModel):
    code: str
    state: str
    code_verifier: str
