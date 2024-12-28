from typing import List, Optional

from fastapi import APIRouter, Depends, Query, Request

from src.app.controllers.role_controller import RoleController
from src.app.decorators.auth_decorator import require_permissions
from src.app.dependencies.role import get_role_controller
from src.app.schemas.requests.role import (
    AssignProjectRoleRequest,
    AssignSystemRoleRequest,
    RoleCreateRequest,
    RoleUpdateRequest,
)
from src.app.schemas.responses.role import PaginatedUserRoleAssignmentResponse, RoleResponse

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
# @require_permissions(system_roles=["user"])
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


@router.post("/system")
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


@router.get("/projects/{project_id}", response_model=PaginatedUserRoleAssignmentResponse)
# @require_permissions(project_roles=["project_owner"])
async def get_project_roles(
    request: Request,
    project_id: int,
    page: int = Query(1, ge=1, description="Page number (starts from 1)"),
    page_size: int = Query(
        10, ge=1, le=100, description="Number of items per page"),
    role_name: Optional[str] = Query(None, description="Filter by role name"),
    search: Optional[str] = Query(
        None, description="Search by user name or email"),
    controller: RoleController = Depends(get_role_controller)
):
    """Get all user role assignments for a specific project with pagination and filters.

    Args:
        request: FastAPI request object
        project_id: ID of the project
        page: Page number (starts from 1)
        page_size: Number of items per page (1-100)
        role_name: Optional filter by role name
        search: Optional search term for user name or email
        controller: Role controller instance

    Returns:
        Paginated list of user role assignments
    """
    return await controller.get_project_role_assignments(
        project_id=project_id,
        page=page,
        page_size=page_size,
        role_name=role_name,
        search=search
    )


@router.post("/projects/{project_id}")
@require_permissions(project_roles=["project_owner"])
async def assign_project_roles(
    request: Request,
    project_id: int,
    assignments: List[AssignProjectRoleRequest],
    controller: RoleController = Depends(get_role_controller)
):
    """Assign or update roles for multiple users in a project.

    Args:
        request: FastAPI request object
        project_id: ID of the project
        assignments: List of role assignments
        controller: Role controller instance
    """
    await controller.assign_project_roles(project_id, assignments)
    return {"message": "Roles assigned successfully"}
