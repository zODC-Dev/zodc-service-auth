from typing import List

from fastapi import APIRouter, Depends, Request

from src.app.controllers.role_controller import RoleController
from src.app.decorators.auth_decorator import require_permissions
from src.app.dependencies.role import get_role_controller
from src.app.schemas.requests.role import (
    AssignProjectRoleRequest,
    AssignSystemRoleRequest,
    RoleCreateRequest,
    RoleUpdateRequest,
)
from src.app.schemas.responses.role import RoleResponse

router = APIRouter()


@router.post("/", response_model=RoleResponse)
@require_permissions(system_roles=["admin"], permissions=["system.roles.manage"])
async def create_role(
    request: Request,
    role_data: RoleCreateRequest,
    controller: RoleController = Depends(get_role_controller)
):
    """Create a new role.

    Args:
        request: FastAPI request object
        role_data: Role creation data
        controller: Role controller instance

    Returns:
        Created role response
    """
    return await controller.create_role(role_data)


@router.get("/", response_model=List[RoleResponse])
@require_permissions(system_roles=["user"])
async def get_roles(
    request: Request,
    include_deleted: bool = False,
    controller: RoleController = Depends(get_role_controller)
):
    """Get all roles.

    Args:
        request: FastAPI request object
        include_deleted: Whether to include deleted roles
        controller: Role controller instance

    Returns:
        List of role responses
    """
    return await controller.get_roles(include_deleted)


@router.put("/{role_id}", response_model=RoleResponse)
@require_permissions(system_roles=["admin"], permissions=["system.roles.manage"])
async def update_role(
    request: Request,
    role_id: int,
    role_data: RoleUpdateRequest,
    controller: RoleController = Depends(get_role_controller)
):
    """Update an existing role.

    Args:
        request: FastAPI request object
        role_id: ID of the role to update
        role_data: Role update data
        controller: Role controller instance

    Returns:
        Updated role response
    """
    return await controller.update_role(role_id, role_data)


@router.post("/assign/system")
@require_permissions(system_roles=["admin"], permissions=["system.roles.manage"])
async def assign_system_role(
    request: Request,
    role_data: AssignSystemRoleRequest,
    controller: RoleController = Depends(get_role_controller)
):
    """Assign a system role to a user.

    Args:
        request: FastAPI request object
        role_data: Role assignment data
        controller: Role controller instance
    """
    await controller.assign_system_role(role_data)
    return {"message": "Role assigned successfully"}


@router.post("/assign/project")
@require_permissions(system_roles=["admin"], permissions=["system.roles.manage"])
async def assign_project_role(
    request: Request,
    role_data: AssignProjectRoleRequest,
    controller: RoleController = Depends(get_role_controller)
):
    """Assign a project role to a user.

    Args:
        request: FastAPI request object
        role_data: Role assignment data
        controller: Role controller instance
    """
    await controller.assign_project_role(role_data)
    return {"message": "Role assigned successfully"}
