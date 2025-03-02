from typing import Dict, List, Optional

from pydantic import BaseModel, EmailStr

from src.app.schemas.requests.base import BaseRequest


class LoginEmailPasswordRequest(BaseRequest):
    email: EmailStr
    password: str


class LoginSSORequest(BaseRequest):
    code_challenge: str


class LoginSSOCallbackRequest(BaseRequest):
    code: str
    state: str
    code_verifier: str


class LoginJiraRequest(BaseRequest):
    pass


class LoginJiraCallbackRequest(BaseRequest):
    code: str


class TokenVerificationRequest(BaseModel):
    token: str
    permission: Optional[str] = None
    project_id: Optional[int] = None
    required_system_roles: Optional[List[str]] = None
    required_project_roles: Optional[List[str]] = None
    require_all_roles: bool = False


class RefreshTokenRequest(BaseRequest):
    refresh_token: str

class JWTClaims(BaseModel):
    sub: str
    email: str
    name: str
    system_role: str
    system_permissions: List[str]
    project_roles: Dict[str, str]
    project_permissions: Dict[str, List[str]]
    is_jira_linked: bool
    exp: int
    iat: int
    iss: str
