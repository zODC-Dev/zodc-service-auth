from datetime import datetime
from typing import Any, Dict, List, Optional

from src.app.schemas.responses.base import BaseResponse
from src.domain.entities.user import User


class UserResponse(BaseResponse):
    id: int
    email: str
    name: Optional[str]
    system_role: Optional[str] = None
    is_active: bool
    created_at: datetime
    is_jira_linked: bool
    is_system_user: bool
    permission_names: List[str]
    project_roles: List[Dict[str, Any]] = []
    avatar_url: Optional[str] = None

    @classmethod
    def from_domain(cls, user: User) -> "UserResponse":
        project_roles = []
        if user.user_project_roles:
            for upr in user.user_project_roles:
                if upr.project and upr.role:
                    permission_names = []
                    if upr.role.permissions:
                        permission_names = [p.name for p in upr.role.permissions]

                    project_roles.append({
                        "projectKey": upr.project.key,
                        "role": upr.role.name,
                        "permissionNames": permission_names
                    })

        return cls(
            id=user.id,
            email=user.email,
            name=user.name,
            system_role=user.system_role.name if user.system_role else None,
            is_active=user.is_active,
            created_at=user.created_at,
            is_jira_linked=user.is_jira_linked,
            is_system_user=user.is_system_user,
            permission_names=[
                p.name for p in user.system_role.permissions] if user.system_role and user.system_role.permissions else [],
            project_roles=project_roles,
            avatar_url=user.avatar_url
        )
