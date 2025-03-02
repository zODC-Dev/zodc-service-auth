from typing import Dict, List

from sqlmodel import or_, select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.domain.entities.permission import Permission as PermissionEntity
from src.domain.repositories.permission_repository import IPermissionRepository
from src.domain.value_objects.permissions import ProjectPermission, SystemPermission
from src.infrastructure.models.permission import Permission
from src.infrastructure.models.project import Project
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

    async def get_system_permissions_by_user_id(self, user_id: int) -> SystemPermission:
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
        return SystemPermission(permissions=[self._to_domain(p) for p in result.all()])

    async def get_permissions_of_all_projects_by_user_id(
        self,
        user_id: int
    ) -> List[ProjectPermission]:
        """Get user's permissions of all projects"""
        # Query to get permissions of all projects by user id
        stmt = (
            select(Permission, Project)
            .join(RolePermission, Permission.id == RolePermission.permission_id)  # type: ignore
            .join(UserProjectRole, RolePermission.role_id == UserProjectRole.role_id)  # type: ignore
            .join(Project, UserProjectRole.project_id == Project.id)  # type: ignore
            .where(UserProjectRole.user_id == user_id)
        )

        result = await self.session.exec(stmt)
        records = list(result.all())

        # Group permissions by project
        project_permissions: Dict[int, List[PermissionEntity]] = {}
        project_names: Dict[int, str] = {}

        for permission, project in records:
            if project.id is None:
                continue
            if project.id not in project_permissions:
                project_permissions[project.id] = []
                project_names[project.id] = project.name
            project_permissions[project.id].append(self._to_domain(permission))

        # Convert to list of ProjectPermission objects
        return [
            ProjectPermission(
                project_id=project_id,
                project_name=project_names[project_id],
                permissions=permissions
            )
            for project_id, permissions in project_permissions.items()
        ]

    async def get_permissions_of_project_by_user_id(
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

    async def get_permissions_by_ids(self, permission_ids: List[int]) -> List[PermissionEntity]:
        stmt = select(Permission).where(Permission.id.in_(permission_ids))  # type: ignore
        result = await self.session.exec(stmt)
        return [self._to_domain(p) for p in result.all()]

    def _to_domain(self, permission: Permission) -> PermissionEntity:
        return PermissionEntity(
            id=permission.id,
            name=permission.name,
            description=permission.description,
            group=permission.group
        )
