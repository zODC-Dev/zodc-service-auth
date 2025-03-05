from typing import List, Optional

from src.app.schemas.responses.base import BaseResponse
from src.domain.entities.project import Project
from src.domain.entities.user_project_role import UserProjectRole


class ProjectResponse(BaseResponse):
    id: int
    name: str
    key: str
    description: str
    avatar_url: Optional[str] = None
    is_jira_linked: bool = True

    @classmethod
    def from_domain(cls, project: Project) -> 'ProjectResponse':
        return cls(
            id=project.id,
            name=project.name,
            key=project.key,
            description=project.description,
            avatar_url=project.avatar_url,
            is_jira_linked=True
        )


class ProjectUserWithRoleResponse(BaseResponse):
    user_id: int
    name: str
    email: str
    # role_id: int
    role_name: str

    @classmethod
    def from_domain(cls, user_project_role: UserProjectRole) -> 'ProjectUserWithRoleResponse':
        return cls(
            user_id=user_project_role.user.id if user_project_role.user else None,
            name=user_project_role.user.name if user_project_role.user else None,
            email=user_project_role.user.email if user_project_role.user else None,
            # role_id=user_project_role.role.id if user_project_role.role else None,
            role_name=user_project_role.role.name if user_project_role.role else None
        )


class PaginatedProjectUsersWithRolesResponse(BaseResponse):
    items: List[ProjectUserWithRoleResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

    @classmethod
    def from_domain(cls, user_project_roles: List[UserProjectRole], total: int, page: int, page_size: int, total_pages: int) -> 'PaginatedProjectUsersWithRolesResponse':
        return cls(
            items=[ProjectUserWithRoleResponse.from_domain(upr) for upr in user_project_roles],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
