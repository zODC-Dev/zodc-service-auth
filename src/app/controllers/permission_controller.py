from typing import List

from src.app.schemas.responses.permission import PermissionResponse
from src.app.services.permission_service import PermissionService


class PermissionController:
    def __init__(self, permission_service: PermissionService):
        self.permission_service = permission_service

    async def get_permissions(self) -> List[PermissionResponse]:
        permissions = await self.permission_service.get_all_permissions()
        return [PermissionResponse.from_domain(permission) for permission in permissions]
