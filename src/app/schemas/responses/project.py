from typing import List

from src.app.schemas.responses.base import BaseResponse
from src.domain.entities.project import Project
from src.domain.entities.user_project_role import UserProjectRole


class ProjectResponse(BaseResponse):
    id: int
    name: str
    key: str
    description: str

    @classmethod
    def from_domain(cls, project: Project) -> 'ProjectResponse':
        return cls(
            id=project.id,
            name=project.name,
            key=project.key,
            description=project.description
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


class ProjectUsersWithRolesResponse(BaseResponse):
    items: List[ProjectUserWithRoleResponse]

    @classmethod
    def from_domain(cls, user_project_roles: List[UserProjectRole]) -> 'ProjectUsersWithRolesResponse':
        return cls(
            items=[ProjectUserWithRoleResponse.from_domain(upr) for upr in user_project_roles]
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
