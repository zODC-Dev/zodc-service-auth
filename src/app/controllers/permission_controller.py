from fastapi import HTTPException

from src.app.schemas.requests.permission import PermissionVerificationRequest
from src.app.schemas.responses.permission import GroupedPermissionResponse, PermissionVerificationResponse
from src.app.services.permission_service import PermissionService


class PermissionController:
    def __init__(self, permission_service: PermissionService):
        self.permission_service = permission_service

    async def get_permissions(self) -> GroupedPermissionResponse:
        permissions = await self.permission_service.get_all_permissions()
        return GroupedPermissionResponse.from_domain(permissions)

    async def verify_permission(
        self,
        request: PermissionVerificationRequest
    ) -> PermissionVerificationResponse:
        verification_result = await self.permission_service.verify_permission(
            PermissionVerificationRequest.to_domain(request))
        if verification_result.error:
            raise HTTPException(
                status_code=401, detail=verification_result.error)
        return PermissionVerificationResponse.from_domain(verification_result)
