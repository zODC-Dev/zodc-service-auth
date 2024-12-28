from src.app.schemas.responses.permission import GroupedPermissionResponse
from src.app.services.permission_service import PermissionService


class PermissionController:
    def __init__(self, permission_service: PermissionService):
        self.permission_service = permission_service

    async def get_permissions(self) -> GroupedPermissionResponse:
        permissions = await self.permission_service.get_all_permissions()
        return GroupedPermissionResponse.from_domain(permissions)
