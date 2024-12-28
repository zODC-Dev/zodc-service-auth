from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from src.app.schemas.requests.role import AssignProjectRoleRequest, RoleCreateRequest, RoleUpdateRequest
from src.domain.entities.role import Role, RoleCreate as DomainRoleCreate, RoleUpdate as DomainRoleUpdate
from src.domain.entities.user_project_role import UserProjectRole
from src.domain.exceptions.project_exceptions import ProjectNotFoundError
from src.domain.exceptions.role_exceptions import (
    InvalidPermissionsError,
    RoleError,
    RoleIsSystemRoleError,
    RoleNotFoundError,
)
from src.domain.exceptions.user_exceptions import UserNotFoundError
from src.domain.repositories.permission_repository import IPermissionRepository
from src.domain.repositories.project_repository import IProjectRepository
from src.domain.repositories.role_repository import IRoleRepository
from src.domain.repositories.user_repository import IUserRepository


@dataclass
class PaginatedResult:
    items: List[Dict[str, Any]]
    total: int
    page: int
    page_size: int
    total_pages: int


class RoleService:
    def __init__(
        self,
        role_repository: IRoleRepository,
        permission_repository: IPermissionRepository,
        project_repository: IProjectRepository,
        user_repository: IUserRepository
    ):
        self.role_repository = role_repository
        self.permission_repository = permission_repository
        self.project_repository = project_repository
        self.user_repository = user_repository

    async def create_role(self, role_data: RoleCreateRequest) -> Role:
        # Convert permission_ids to permission_names
        if role_data.permission_names:
            permissions = await self.permission_repository.get_permissions_by_names(
                role_data.permission_names
            )
            # Check if all requested permissions were found
            found_names = {p.name for p in permissions}
            missing_names = set(role_data.permission_names) - found_names
            if missing_names:
                raise InvalidPermissionsError(list(missing_names))

        # Convert to domain model
        domain_role_data = DomainRoleCreate(
            name=role_data.name,
            description=role_data.description,
            is_system_role=role_data.is_system_role,
            permission_names=role_data.permission_names
        )

        return await self.role_repository.create_role(domain_role_data)

    async def update_role(self, role_id: int, role_data: RoleUpdateRequest) -> Role:
        # Convert to domain model
        domain_role_data = DomainRoleUpdate(
            name=role_data.name,
            description=role_data.description,
            is_active=role_data.is_active,
            is_system_role=role_data.is_system_role,
            permission_names=role_data.permission_names if role_data.permission_names else None
        )

        return await self.role_repository.update_role(role_id, domain_role_data)

    async def get_all_roles(self, include_deleted: bool = False) -> List[Role]:
        return await self.role_repository.get_all_roles(include_deleted)

    async def delete_role(self, role_id: int) -> Role:
        return await self.role_repository.delete_role(role_id)

    async def assign_system_role(self, user_id: int, role_name: str) -> None:
        # Verify role exists before assignment
        role = await self.role_repository.get_role_by_name(role_name)
        if not role:
            raise RoleNotFoundError(role_name=role_name)
        if not role.is_system_role:
            raise RoleError(f"Role '{role_name}' is not a system role")

        await self.role_repository.assign_system_role_to_user(user_id, role_name)

    async def get_project_roles_by_project_id(
        self,
        project_id: int,
        page: int = 1,
        page_size: int = 10,
        role_name: Optional[str] = None,
        search: Optional[str] = None
    ) -> Tuple[List[UserProjectRole], int]:
        # Verify project exists
        project = await self.project_repository.get_project_by_id(project_id)
        if not project:
            raise ProjectNotFoundError(
                f"Project with id {project_id} not found")

        # Get paginated assignments
        return await self.role_repository.get_project_roles_by_project_id(
            project_id=project_id,
            page=page,
            page_size=page_size,
            role_name=role_name,
            search=search
        )

    async def assign_project_role(self, project_id: int, assignment: AssignProjectRoleRequest) -> None:
        """Assign or update roles for multiple users in a project"""
        # Verify project exists
        project = await self.project_repository.get_project_by_id(project_id)
        if not project:
            raise ProjectNotFoundError(
                f"Project with id {project_id} not found")

        # Verify role exists
        role = await self.role_repository.get_role_by_name(assignment.role_name)
        if not role:
            raise RoleNotFoundError(role_name=assignment.role_name)

        # Verify role is not system role
        if role.is_system_role:
            raise RoleIsSystemRoleError(assignment.role_name)

        # Verify user exists
        user = await self.user_repository.get_user_by_id(assignment.user_id)
        if not user:
            raise UserNotFoundError(
                f"User with id {assignment.user_id} not found")

        # Assign role
        await self.role_repository.assign_project_role_to_user(
            user_id=assignment.user_id,
            project_id=project_id,
            role_name=assignment.role_name
        )

    async def get_system_roles(
        self,
        page: int = 1,
        page_size: int = 10,
        search: Optional[str] = None,
        sort_by: Optional[str] = None,
        sort_order: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> Tuple[List[Role], int]:
        return await self.role_repository.get_system_roles(
            page=page,
            page_size=page_size,
            search=search,
            sort_by=sort_by,
            sort_order=sort_order,
            is_active=is_active
        )
