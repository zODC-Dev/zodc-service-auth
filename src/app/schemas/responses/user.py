from datetime import datetime
from typing import Any, Dict, List, Optional

from src.app.schemas.responses.base import BaseResponse
from src.domain.entities.user import User


# Add new model for project roles
class ProjectRoleInfo(BaseResponse):
    project_key: str
    roles: List[str]
    permission_names: List[str]


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
    project_roles: List[ProjectRoleInfo] = []
    avatar_url: Optional[str] = None

    @classmethod
    def from_domain(cls, user: User) -> "UserResponse":
        # Create a map to group roles by project
        project_roles_map: Dict[str, Any] = {}

        if user.user_project_roles:
            for upr in user.user_project_roles:
                if upr.project and upr.role:
                    project_key = upr.project.key
                    if project_key not in project_roles_map:
                        project_roles_map[project_key] = {
                            "roles": [],
                            "permission_names": set()
                        }

                    # Add role name
                    project_roles_map[project_key]["roles"].append(upr.role.name)

                    # Add permissions from this role
                    if upr.role.permissions:
                        project_roles_map[project_key]["permission_names"].update(
                            p.name for p in upr.role.permissions
                        )

        # Convert map to list of ProjectRoleInfo
        project_roles = [
            ProjectRoleInfo(
                project_key=project_key,
                roles=info["roles"],
                permission_names=list(info["permission_names"])
            )
            for project_key, info in project_roles_map.items()
        ]

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
                p.name for p in user.system_role.permissions
            ] if user.system_role and user.system_role.permissions else [],
            project_roles=project_roles,
            avatar_url=user.avatar_url
        )
