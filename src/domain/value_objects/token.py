from typing import Dict, List

from pydantic import BaseModel


class TokenPayload(BaseModel):
    sub: str
    email: str
    name: str
    system_role: str
    system_permissions: List[str]
    project_roles: Dict[str, str]
    project_permissions: Dict[str, List[str]]
