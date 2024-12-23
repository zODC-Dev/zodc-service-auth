from typing import List

from src.domain.entities.permission import Permission
from src.domain.repositories.permission_repository import IPermissionRepository


class PermissionService:
    def __init__(self, permission_repository: IPermissionRepository):
        self.permission_repository = permission_repository

    async def get_all_permissions(self) -> List[Permission]:
        return await self.permission_repository.get_all_permissions()
