
from fastapi import APIRouter, Depends, Request

from src.app.controllers.permission_controller import PermissionController
from src.app.dependencies.permission import get_permission_controller
from src.app.schemas.requests.permission import PermissionVerificationRequest
from src.app.schemas.responses.permission import GroupedPermissionResponse, PermissionVerificationResponse

router = APIRouter()


@router.get("/", response_model=GroupedPermissionResponse)
# @require_permissions(system_roles=["user"])
async def get_permissions(
    request: Request,
    controller: PermissionController = Depends(get_permission_controller)
):
    """Get all available permissions in the system.

    Args:
        request: FastAPI request object
        controller: Permission controller instance

    Returns:
        List of permission responses
    """
    return await controller.get_permissions()


@router.post("/verify", response_model=PermissionVerificationResponse)
async def verify_permission(
    request: PermissionVerificationRequest,
    controller: PermissionController = Depends(get_permission_controller)
):
    """Verify if a user has ALL permissions in given scope

    This endpoint is for internal service communication
    """
    return await controller.verify_permission(request)
