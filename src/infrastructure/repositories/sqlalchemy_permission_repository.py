from typing import List

from sqlmodel import or_, select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.domain.entities.permission import Permission as PermissionEntity
from src.domain.repositories.permission_repository import IPermissionRepository
from src.infrastructure.models.permission import Permission
from src.infrastructure.models.role import Role
from src.infrastructure.models.role_permission import RolePermission
from src.infrastructure.models.user import User
from src.infrastructure.models.user_project_role import UserProjectRole


class SQLAlchemyPermissionRepository(IPermissionRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all_permissions(self) -> List[PermissionEntity]:
        result = await self.session.exec(select(Permission))
        permissions = result.all()
        return [self._to_domain(p) for p in permissions]

    async def get_permissions_by_names(self, permission_names: List[str]) -> List[PermissionEntity]:
        stmt = select(Permission).where(
            or_(*[Permission.name == name for name in permission_names]))
        result = await self.session.exec(stmt)
        permissions = result.all()
        return [self._to_domain(p) for p in permissions]

    async def get_user_system_permissions(self, user_id: int) -> List[PermissionEntity]:
        """Get user's system permissions through their system role"""
        # Query to get permissions through user's system role
        stmt = (
            select(Permission)
            .join(RolePermission, Permission.id == RolePermission.permission_id)  # type: ignore
            .join(Role, RolePermission.role_id == Role.id)  # type: ignore
            .join(User, Role.id == User.role_id)  # type: ignore
            .where(User.id == user_id, Role.is_system_role)
        )

        result = await self.session.exec(stmt)
        return [self._to_domain(p) for p in result.all()]

    async def get_user_project_permissions(
        self,
        user_id: int,
        project_id: int
    ) -> List[PermissionEntity]:
        """Get user's project permissions through their project roles"""
        # Query to get permissions through user's project roles
        stmt = (
            select(Permission)
            .join(Role.permissions)  # type: ignore
            .join(UserProjectRole, Role.id == UserProjectRole.role_id)  # type: ignore
            .where(
                UserProjectRole.user_id == user_id,
                UserProjectRole.project_id == project_id,
                Role.is_active,
                not Role.is_system_role
            )
        )

        result = await self.session.exec(stmt)
        return [self._to_domain(p) for p in result.all()]

    def _to_domain(self, permission: Permission) -> PermissionEntity:
        return PermissionEntity(
            id=permission.id,
            name=permission.name,
            description=permission.description,
            group=permission.group
        )
