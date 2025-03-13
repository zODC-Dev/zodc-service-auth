from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from src.app.schemas.requests.role import RoleCreateRequest, RoleUpdateRequest
from src.domain.entities.role import Role, RoleCreate as DomainRoleCreate, RoleUpdate as DomainRoleUpdate
from src.domain.entities.user_project_role import UserProjectRole
from src.domain.exceptions.project_exceptions import ProjectNotFoundError
from src.domain.exceptions.role_exceptions import (
    InvalidPermissionIdsError,
    RoleError,
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
        if role_data.permissions:
            permissions = await self.permission_repository.get_permissions_by_ids(
                role_data.permissions
            )
            # Check if all requested permissions were found
            found_ids = {p.id for p in permissions}
            missing_ids = set(role_data.permissions) - found_ids
            if missing_ids:
                raise InvalidPermissionIdsError(list(missing_ids))

        # Convert to domain model
        domain_role_data = DomainRoleCreate(
            name=role_data.name,
            description=role_data.description,
            is_system_role=role_data.is_system_role,
            permissions=role_data.permissions
        )

        return await self.role_repository.create_role(domain_role_data)

    async def update_role(self, role_id: int, role_data: RoleUpdateRequest) -> Role:
        # Kiểm tra permissions nếu được cung cấp
        if role_data.permissions:
            permissions = await self.permission_repository.get_permissions_by_ids(
                role_data.permissions
            )
            # Kiểm tra xem tất cả permissions yêu cầu có tồn tại không
            found_ids = {p.id for p in permissions}
            missing_ids = set(role_data.permissions) - found_ids
            if missing_ids:
                raise InvalidPermissionIdsError(list(missing_ids))

        # Chuyển đổi sang domain model
        domain_role_data = DomainRoleUpdate(
            name=role_data.name,
            description=role_data.description,
            is_active=role_data.is_active,
            is_system_role=role_data.is_system_role,
            permissions=role_data.permissions if role_data.permissions else None
        )

        return await self.role_repository.update_role(role_id, domain_role_data)

    async def get_all_roles(
        self,
        page: int = 1,
        page_size: int = 10,
        search: Optional[str] = None,
        sort_by: Optional[str] = None,
        sort_order: Optional[str] = None,
        is_active: Optional[bool] = None,
        is_system_role: Optional[bool] = None
    ) -> Tuple[List[Role], int]:
        """Get paginated, filtered and sorted roles"""
        return await self.role_repository.get_all_roles(
            page=page,
            page_size=page_size,
            search=search,
            sort_by=sort_by,
            sort_order=sort_order,
            is_active=is_active,
            is_system_role=is_system_role
        )

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

    # async def assign_project_role(self, project_id: int, assignment: AssignProjectRoleRequest) -> None:
    #     """Assign or update roles for multiple users in a project"""
    #     # Verify project exists
    #     project = await self.project_repository.get_project_by_id(project_id)
    #     if not project:
    #         raise ProjectNotFoundError(
    #             f"Project with id {project_id} not found")

    #     # Verify role exists
    #     role = await self.role_repository.get_role_by_name(assignment.role_name)
    #     if not role:
    #         raise RoleNotFoundError(role_name=assignment.role_name)

    #     # Verify role is not system role
    #     if role.is_system_role:
    #         raise RoleIsSystemRoleError(assignment.role_name)

    #     # Verify user exists
    #     user = await self.user_repository.get_user_by_id(assignment.user_id)
    #     if not user:
    #         raise UserNotFoundError(
    #             f"User with id {assignment.user_id} not found")

    #     # Assign role
    #     await self.role_repository.assign_project_role_to_user(
    #         user_id=assignment.user_id,
    #         project_id=project_id,
    #         role_name=assignment.role_name
    #     )

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

    async def get_all_roles_without_pagination(
        self,
        is_active: Optional[bool] = None
    ) -> List[Role]:
        """Get all roles without pagination, filtering only by is_active"""
        # We can reuse the existing get_all_roles method but ignore pagination and other filters
        roles, _ = await self.role_repository.get_all_roles(
            page=1,
            # Set a very large page size to effectively get all roles
            page_size=10000,
            search=None,
            sort_by=None,
            sort_order=None,
            is_active=is_active,
            is_system_role=None
        )
        return roles

    async def assign_project_roles(
        self,
        project_id: int,
        user_id: int,
        role_ids: List[int]
    ) -> None:
        """Assign project roles to a user.

        This will remove all existing roles for the user in this project and assign the new roles.

        Args:
            project_id: ID of the project
            user_id: ID of the user
            role_ids: List of role IDs to assign

        Raises:
            UserNotFoundError: If the user doesn't exist
            ProjectNotFoundError: If the project doesn't exist
            RoleNotFoundError: If any of the roles don't exist
        """
        # Check if user exists
        user = await self.user_repository.get_user_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"User with id {user_id} not found")

        # Check if project exists
        project = await self.project_repository.get_project_by_id(project_id)
        if not project:
            raise ProjectNotFoundError(f"Project with id {project_id} not found")

        # Check if all roles exist
        for role_id in role_ids:
            role = await self.role_repository.get_role_by_id(role_id)
            if not role:
                raise RoleNotFoundError(role_id=role_id)

        # Remove all existing roles for this user in this project
        await self.role_repository.remove_user_project_roles(
            user_id=user_id,
            project_id=project_id
        )

        # Assign new roles
        for role_id in role_ids:
            await self.role_repository.create_user_project_role(
                user_id=user_id,
                project_id=project_id,
                role_id=role_id
            )
