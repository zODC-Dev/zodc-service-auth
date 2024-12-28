from typing import List

from sqlmodel import or_, select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.domain.entities.permission import Permission as PermissionEntity
from src.domain.repositories.permission_repository import IPermissionRepository
from src.infrastructure.models.permission import Permission


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

    def _to_domain(self, permission: Permission) -> PermissionEntity:
        return PermissionEntity(
            id=permission.id,
            name=permission.name,
            description=permission.description,
            group=permission.group
        )
