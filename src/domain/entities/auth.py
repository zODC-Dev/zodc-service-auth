from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserCredentials(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)

class AuthToken(BaseModel):
    access_token: str
    expires_at: datetime
    token_type: str = "bearer"
    refresh_token: Optional[str] = None

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
