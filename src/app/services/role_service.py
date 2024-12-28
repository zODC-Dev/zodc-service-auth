from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from src.app.schemas.requests.role import AssignProjectRoleRequest, RoleCreateRequest, RoleUpdateRequest
from src.app.schemas.responses.common import PaginatedResponse
from src.app.schemas.responses.role import UserRoleAssignmentResponse
from src.domain.entities.role import Role, RoleCreate as DomainRoleCreate, RoleUpdate as DomainRoleUpdate
from src.domain.exceptions.project_exceptions import ProjectNotFoundError
from src.domain.exceptions.role_exceptions import InvalidPermissionsError, RoleError, RoleNotFoundError
from src.domain.exceptions.user_exceptions import UserNotFoundError
from src.domain.repositories.permission_repository import IPermissionRepository
from src.domain.repositories.role_repository import IRoleRepository


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
        permission_repository: IPermissionRepository
    ):
        self.role_repository = role_repository
        self.permission_repository = permission_repository

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
            permission_names=role_data.permission_names if role_data.permission_names else None
        )

        return await self.role_repository.update_role(role_id, domain_role_data)

    async def get_all_roles(self, include_deleted: bool = False) -> List[Role]:
        return await self.role_repository.get_all_roles(include_deleted)

    async def assign_system_role(self, user_id: int, role_name: str) -> None:
        # Verify role exists before assignment
        role = await self.role_repository.get_role_by_name(role_name)
        if not role:
            raise RoleNotFoundError(role_name=role_name)
        if not role.is_system_role:
            raise RoleError(f"Role '{role_name}' is not a system role")

        await self.role_repository.assign_system_role_to_user(user_id, role_name)

    async def get_project_role_assignments(
        self,
        project_id: int,
        page: int = 1,
        page_size: int = 10,
        role_name: Optional[str] = None,
        search: Optional[str] = None
    ) -> PaginatedResponse[UserRoleAssignmentResponse]:
        # Verify project exists
        project = await self.role_repository.get_project_by_id(project_id)
        if not project:
            raise ProjectNotFoundError(
                f"Project with id {project_id} not found")

        # Get paginated assignments
        assignments, total = await self.role_repository.get_project_role_assignments(
            project_id=project_id,
            page=page,
            page_size=page_size,
            role_name=role_name,
            search=search
        )

        # Format assignments using Pydantic model
        formatted_assignments = []
        for assignment in assignments:
            user = assignment.user
            if not user:
                continue

            formatted_assignments.append(
                UserRoleAssignmentResponse(
                    user_id=user.id,
                    user_name=user.name or "",
                    user_email=user.email,
                    role_name=assignment.role.name if assignment.role else None
                )
            )

        return PaginatedResponse[UserRoleAssignmentResponse](
            items=formatted_assignments,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=(total + page_size - 1) // page_size
        )

    async def assign_project_roles(self, project_id: int, assignments: List[AssignProjectRoleRequest]) -> None:
        """Assign or update roles for multiple users in a project"""
        # Verify project exists
        project = await self.role_repository.get_project_by_id(project_id)
        if not project:
            raise ProjectNotFoundError(
                f"Project with id {project_id} not found")

        # Process each assignment
        for assignment in assignments:
            # Verify role exists
            role = await self.role_repository.get_role_by_name(assignment.role_name)
            if not role:
                raise RoleNotFoundError(role_name=assignment.role_name)

            # Verify user exists
            user = await self.role_repository.get_user_by_id(assignment.user_id)
            if not user:
                raise UserNotFoundError(
                    f"User with id {assignment.user_id} not found")

            # Assign role
            await self.role_repository.assign_project_role_to_user(
                user_id=assignment.user_id,
                project_id=project_id,
                role_name=assignment.role_name
            )
