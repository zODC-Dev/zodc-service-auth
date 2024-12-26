from typing import List, Optional

from sqlmodel import or_, select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.domain.entities.permission import Permission as PermissionEntity
from src.domain.entities.role import Role as RoleEntity, RoleCreate, RoleUpdate
from src.domain.exceptions.role_exceptions import RoleAlreadyExistsError, RoleNotFoundError
from src.domain.repositories.role_repository import IRoleRepository
from src.infrastructure.models.permission import Permission
from src.infrastructure.models.role import Role
from src.infrastructure.models.role_permission import RolePermission
from src.infrastructure.models.user import User
from src.infrastructure.models.user_project_role import UserProjectRole


class SQLAlchemyRoleRepository(IRoleRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_role_by_name(self, name: str) -> Optional[RoleEntity]:
        result = await self.session.exec(
            select(Role).where(Role.name == name)
        )
        role = result.first()
        return self._to_domain(role) if role else None

    async def get_role_permissions(self, role_id: int) -> List[PermissionEntity]:
        result = await self.session.exec(
            select(Permission)
            .join(RolePermission)
            .where(RolePermission.role_id == role_id)
        )
        permissions = result.all()
        return [self._permission_to_domain(p) for p in permissions]

    async def assign_system_role_to_user(self, user_id: int, role_name: str) -> None:
        # Get role
        role_result = await self.session.exec(
            select(Role).where(Role.name == role_name)
        )
        role = role_result.first()
        if not role:
            raise ValueError(f"Role {role_name} not found")

        # Update user's system role
        user_result = await self.session.exec(
            select(User).where(User.id == user_id)
        )
        user = user_result.first()
        if not user:
            raise ValueError(f"User {user_id} not found")

        user.role_id = role.id
        await self.session.commit()

    async def assign_project_role_to_user(
        self,
        user_id: int,
        project_id: int,
        role_name: str
    ) -> None:
        # Get role
        role_result = await self.session.exec(
            select(Role).where(Role.name == role_name)
        )
        role = role_result.first()
        if not role:
            raise ValueError(f"Role {role_name} not found")

        # Create or update project role
        user_project_role = UserProjectRole(
            user_id=user_id,
            project_id=project_id,
            role_id=role.id
        )
        self.session.add(user_project_role)
        await self.session.commit()

    async def get_user_system_role(self, user_id: int) -> Optional[RoleEntity]:
        result = await self.session.exec(
            select(Role)
            .join(User)
            .where(User.id == user_id)
        )
        role = result.first()
        return self._to_domain(role) if role else None

    async def get_user_project_roles(
        self,
        user_id: int,
        project_id: Optional[int] = None
    ) -> List[RoleEntity]:
        query = select(Role).join(UserProjectRole)

        if project_id:
            query = query.where(
                UserProjectRole.user_id == user_id,
                UserProjectRole.project_id == project_id
            )
        else:
            query = query.where(UserProjectRole.user_id == user_id)

        result = await self.session.exec(query)
        roles = result.all()
        return [self._to_domain(r) for r in roles]

    async def get_user_permissions(
        self,
        user_id: int,
        project_id: Optional[int] = None
    ) -> List[PermissionEntity]:
        if project_id:
            # Execute queries separately and combine results in Python
            # Get system permissions
            system_perms = await self.session.exec(
                select(Permission)
                .join(RolePermission)
                .join(Role)
                .join(User)
                .where(User.id == user_id)
            )

            # Get project permissions
            project_perms = await self.session.exec(
                select(Permission)
                .join(RolePermission)
                .join(Role)
                .join(UserProjectRole)
                .where(
                    UserProjectRole.user_id == user_id,
                    UserProjectRole.project_id == project_id
                )
            )

            # Convert to lists before combining
            permissions = list(system_perms.all()) + list(project_perms.all())
            # Remove duplicates if needed
            unique_permissions = list({p.id: p for p in permissions}.values())
            return [self._permission_to_domain(p) for p in unique_permissions]
        else:
            # Just get system permissions
            result = await self.session.exec(
                select(Permission)
                .join(RolePermission)
                .join(Role)
                .join(User)
                .where(User.id == user_id)
            )
            permissions = list(result.all())
            return [self._permission_to_domain(p) for p in permissions]

    def _to_domain(self, role: Role) -> RoleEntity:
        return RoleEntity(
            id=role.id,
            name=role.name,
            description=role.description,
            is_system_role=role.is_system_role,
            is_active=role.is_active,
            permissions=[self._permission_to_domain(
                p) for p in role.permissions]
        )

    def _permission_to_domain(self, permission: Permission) -> PermissionEntity:
        return PermissionEntity(
            id=permission.id,
            name=permission.name,
            description=permission.description
        )

    async def get_all_roles(self, include_deleted: bool = False) -> List[RoleEntity]:
        query = select(Role)
        if not include_deleted:
            query = query.where(Role.is_active)
        result = await self.session.exec(query)
        roles = result.all()
        return [self._to_domain(r) for r in roles]

    async def create_role(self, role_data: RoleCreate) -> RoleEntity:
        # Check if role already exists
        existing_role = await self.get_role_by_name(role_data.name)
        if existing_role:
            raise RoleAlreadyExistsError(role_data.name)

        # Create role without permissions first
        role = Role(
            name=role_data.name,
            description=role_data.description or "",
            is_system_role=role_data.is_system_role,
            is_active=role_data.is_active
        )
        self.session.add(role)

        # If permission_names are provided, fetch and link permissions
        if role_data.permission_names:
            # Get permissions by names
            permissions_query = select(Permission).where(
                or_(*[Permission.name == name for name in role_data.permission_names])
            )
            result = await self.session.exec(permissions_query)
            permissions = result.all()

            # Link permissions to role
            role.permissions = list(permissions)

        await self.session.commit()
        await self.session.refresh(role)
        return self._to_domain(role)

    async def update_role(self, role_id: int, role_data: RoleUpdate) -> RoleEntity:
        role = await self.session.get(Role, role_id)
        if not role:
            raise RoleNotFoundError(role_id)

        if role_data.name is not None:
            role.name = role_data.name
        if role_data.description is not None:
            role.description = role_data.description
        if role_data.is_active is not None:
            role.is_active = role_data.is_active
        if role_data.permission_names is not None:
            # Get permissions by names
            permissions_query = select(Permission).where(
                or_(*[Permission.name == name for name in role_data.permission_names])
            )
            result = await self.session.exec(permissions_query)
            permissions = result.all()

            # Update role permissions
            role.permissions = list(permissions)

        await self.session.commit()
        await self.session.refresh(role)
        return self._to_domain(role)

    async def delete_role(self, role_id: int) -> None:
        role = await self.session.get(Role, role_id)
        if not role:
            raise RoleNotFoundError(role_id)
        role.is_active = False
        await self.session.commit()
