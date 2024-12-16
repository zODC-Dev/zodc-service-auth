from typing import List, Optional

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.domain.entities.role import Permission as PermissionEntity, Role as RoleEntity
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
            description=role.description
        )

    def _permission_to_domain(self, permission: Permission) -> PermissionEntity:
        return PermissionEntity(
            id=permission.id,
            name=permission.name,
            description=permission.description
        )
