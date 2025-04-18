from typing import List, Optional

from pydantic import Field

from src.app.schemas.responses.base import BaseResponse
from src.domain.entities.project import Project
from src.domain.entities.user import User
from src.domain.entities.user_project_role import UserProjectRole


class RoleInfo(BaseResponse):
    id: int
    name: str
    description: Optional[str] = None
    is_active: bool = True
    is_system_role: bool = False


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
    roles: List[RoleInfo] = Field(default_factory=list)

    @classmethod
    def from_domain(cls, user_project_role: UserProjectRole) -> 'ProjectAssigneeResponse':
        roles = []
        if hasattr(user_project_role, 'roles') and user_project_role.roles:
            roles = [
                RoleInfo(
                    id=role.id,
                    name=role.name,
                    description=role.description,
                    is_active=role.is_active,
                    is_system_role=role.is_system_role
                ) for role in user_project_role.roles
            ]
        elif user_project_role.role:
            roles = [
                RoleInfo(
                    id=user_project_role.role.id,
                    name=user_project_role.role.name,
                    description=user_project_role.role.description,
                    is_active=user_project_role.role.is_active,
                    is_system_role=user_project_role.role.is_system_role
                )
            ]

        return cls(
            id=user_project_role.user.id if user_project_role.user else None,
            name=user_project_role.user.name if user_project_role.user else None,
            email=user_project_role.user.email if user_project_role.user else None,
            is_system_user=user_project_role.user.is_system_user if user_project_role.user else None,
            avatar_url=user_project_role.user.avatar_url if user_project_role.user else None,
            roles=roles
        )

    @classmethod
    def from_user(cls, user: User) -> 'ProjectAssigneeResponse':
        return cls(
            id=user.id,
            name=user.name,
            email=user.email,
            is_system_user=user.is_system_user,
            avatar_url=user.avatar_url,
            roles=[
                RoleInfo(
                    id=user.system_role.id,
                    name=user.system_role.name,
                    description=user.system_role.description,
                    is_active=user.system_role.is_active,
                    is_system_role=user.system_role.is_system_role
                )
            ] if user.system_role else []
        )


class ProjectUserWithRole(BaseResponse):
    id: int
    name: str
    email: str
    is_system_user: bool
    avatar_url: Optional[str] = None
    roles: List[RoleInfo] = Field(default_factory=list)

    @classmethod
    def from_domain(cls, user_project_role: UserProjectRole) -> 'ProjectUserWithRole':
        roles = []
        if hasattr(user_project_role, 'roles') and user_project_role.roles:
            roles = [
                RoleInfo(
                    id=role.id,
                    name=role.name,
                    description=role.description,
                    is_active=role.is_active,
                    is_system_role=role.is_system_role
                ) for role in user_project_role.roles
            ]
        elif user_project_role.role:
            roles = [
                RoleInfo(
                    id=user_project_role.role.id,
                    name=user_project_role.role.name,
                    description=user_project_role.role.description,
                    is_active=user_project_role.role.is_active,
                    is_system_role=user_project_role.role.is_system_role
                )
            ]

        return cls(
            id=user_project_role.user.id if user_project_role.user else None,
            name=user_project_role.user.name if user_project_role.user else None,
            email=user_project_role.user.email if user_project_role.user else None,
            is_system_user=user_project_role.user.is_system_user if user_project_role.user else None,
            avatar_url=user_project_role.user.avatar_url if user_project_role.user else None,
            roles=roles
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
