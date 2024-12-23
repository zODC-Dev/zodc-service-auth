from typing import List

from src.app.schemas.requests.role import RoleCreateRequest, RoleUpdateRequest
from src.domain.entities.role import Role, RoleCreate as DomainRoleCreate, RoleUpdate as DomainRoleUpdate
from src.domain.exceptions.role_exceptions import InvalidPermissionsError, RoleError, RoleNotFoundError
from src.domain.repositories.permission_repository import IPermissionRepository
from src.domain.repositories.role_repository import IRoleRepository


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

    async def assign_project_role(self, user_id: int, project_id: int, role_name: str) -> None:
        # Verify role exists before assignment
        role = await self.role_repository.get_role_by_name(role_name)
        if not role:
            raise RoleNotFoundError(role_name=role_name)

        await self.role_repository.assign_project_role_to_user(
            user_id=user_id,
            project_id=project_id,
            role_name=role_name
        )
