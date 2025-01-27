from typing import Dict, List

from pydantic import BaseModel


class TokenPayload(BaseModel):
    sub: str
    email: str
    name: str
    system_role: str
    system_permissions: List[str]
    project_roles: Dict[int, str]  # project_id -> role_name
    project_permissions: Dict[int, List[str]]  # project_id -> permissions
