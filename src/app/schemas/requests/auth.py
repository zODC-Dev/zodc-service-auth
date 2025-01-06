from typing import List, Optional

from pydantic import BaseModel, EmailStr


class LoginEmailPasswordRequest(BaseModel):
    email: EmailStr
    password: str


class LoginSSORequest(BaseModel):
    code_challenge: str


class LoginSSOCallbackRequest(BaseModel):
    code: str
    state: str
    code_verifier: str


class TokenVerificationRequest(BaseModel):
    token: str
    permission: Optional[str] = None
    project_id: Optional[int] = None
    required_system_roles: Optional[List[str]] = None
    required_project_roles: Optional[List[str]] = None
    require_all_roles: bool = False
