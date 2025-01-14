from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field

from src.domain.constants.auth import TokenType


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


class RefreshTokenEntity(BaseModel):
    token: str
    user_id: int
    expires_at: datetime
    is_revoked: bool = False
    created_at: datetime = Field(default_factory=datetime.now)
    token_type: TokenType


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class JiraIdentity(BaseModel):
    access_token: str
    refresh_token: Optional[str]
    expires_in: int
    scope: str
