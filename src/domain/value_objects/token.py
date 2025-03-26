from typing import Dict, List

from pydantic import BaseModel


class TokenPayload(BaseModel):
    sub: str
    email: str
    name: str
    system_role: str
    system_permissions: List[str]
    project_roles: Dict[int, List[str]]  # project_id -> list of role names
    project_permissions: Dict[int, List[str]]  # project_id -> permissions
    is_jira_linked: bool
