from typing import List

from fastapi import APIRouter, Depends, Request

from src.app.controllers.permission_controller import PermissionController
from src.app.decorators.auth_decorator import require_permissions
from src.app.dependencies.permission import get_permission_controller
from src.app.schemas.responses.permission import PermissionResponse

router = APIRouter()


@router.get("/", response_model=List[PermissionResponse])
@require_permissions(system_roles=["user"])
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
