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


class ProjectAssigneeResponse(BaseResponse):
    id: int
    name: str
    email: str
    is_system_user: bool
    avatar_url: Optional[str] = None

    @classmethod
    def from_domain(cls, user_project_role: UserProjectRole) -> 'ProjectAssigneeResponse':
        return cls(
            id=user_project_role.user.id if user_project_role.user else None,
            name=user_project_role.user.name if user_project_role.user else None,
            email=user_project_role.user.email if user_project_role.user else None,
            is_system_user=user_project_role.user.is_system_user if user_project_role.user else None,
            avatar_url=user_project_role.user.avatar_url if user_project_role.user else None,
        )


class ProjectUserWithRole(BaseResponse):
    id: int
    name: str
    email: str
    is_system_user: bool
    avatar_url: Optional[str] = None
    role_name: Optional[str] = None

    @classmethod
    def from_domain(cls, user_project_role: UserProjectRole) -> 'ProjectUserWithRole':
        return cls(
            id=user_project_role.user.id if user_project_role.user else None,
            name=user_project_role.user.name if user_project_role.user else None,
            email=user_project_role.user.email if user_project_role.user else None,
            is_system_user=user_project_role.user.is_system_user if user_project_role.user else None,
            avatar_url=user_project_role.user.avatar_url if user_project_role.user else None,
            role_name=user_project_role.role.description if user_project_role.role else None
        )


class PaginatedProjectUsersWithRolesResponse(BaseResponse):
    items: List[ProjectUserWithRole]
    total: int
    page: int
    page_size: int
    total_pages: int

    @classmethod
    def from_domain(cls, user_project_roles: List[UserProjectRole], total: int, page: int, page_size: int, total_pages: int) -> 'PaginatedProjectUsersWithRolesResponse':
        return cls(
            items=[ProjectUserWithRole.from_domain(upr) for upr in user_project_roles],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
