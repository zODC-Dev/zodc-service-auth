
from fastapi import APIRouter, Depends, Request

from src.app.controllers.permission_controller import PermissionController
from src.app.dependencies.permission import get_permission_controller
from src.app.schemas.responses.permission import GroupedPermissionResponse

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
