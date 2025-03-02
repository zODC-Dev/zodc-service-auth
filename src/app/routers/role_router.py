from typing import List, Optional

from fastapi import APIRouter, Depends, Query, Request

from src.app.controllers.role_controller import RoleController
from src.app.dependencies.role import get_role_controller
from src.app.schemas.requests.role import (
    AssignProjectRoleRequest,
    AssignSystemRoleRequest,
    RoleCreateRequest,
    RoleUpdateRequest,
)
from src.app.schemas.responses.base import StandardResponse
from src.app.schemas.responses.role import (
    PaginatedGetProjectRolesResponse,
    PaginatedGetSystemRolesResponse,
    PaginatedRoleResponse,
    RoleResponse,
)

router = APIRouter()


@router.post("", response_model=StandardResponse[RoleResponse],
             responses={
                 400: {"description": "Role already exists or invalid data"},
                 500: {"description": "Internal server error"}
})
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


@router.get("/system", response_model=StandardResponse[PaginatedGetSystemRolesResponse],
            responses={
                500: {"description": "Internal server error"}
})
async def get_system_roles(
    request: Request,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100, alias="pageSize"),
    search: Optional[str] = None,
    sort_by: Optional[str] = Query(
        None, regex="^(name|description|created_at|updated_at)$", alias="sortBy"),
    sort_order: Optional[str] = Query(None, regex="^(asc|desc)$", alias="sortOrder"),
    is_active: Optional[bool] = Query(None, alias="isActive"),
    controller: RoleController = Depends(get_role_controller)
):
    """Get paginated system roles with filtering and sorting.

    Args:
        request: FastAPI request object
        page: Page number
        page_size: Number of items per page
        search: Search term for name and description
        sort_by: Field to sort by
        sort_order: Sort direction (asc/desc)
        is_active: Filter by active status
        controller: Role controller instance

    Returns:
        Paginated list of system roles
    """
    return await controller.get_system_roles(
        page=page,
        page_size=page_size,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
        is_active=is_active
    )


@router.get(
    "",
    response_model=StandardResponse[PaginatedRoleResponse],
    summary="Get all roles with pagination, filtering and sorting"
)
async def get_all_roles(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page", alias="pageSize"),
    search: Optional[str] = Query(None, description="Search in name and description"),
    sort_by: Optional[str] = Query(
        None, description="Field to sort by (name, created_at, updated_at, is_active, is_system_role)", alias="sortBy"),
    sort_order: Optional[str] = Query(None, description="Sort order (asc or desc)", alias="sortOrder"),
    is_active: Optional[bool] = Query(None, description="Filter by active status", alias="isActive"),
    is_system_role: Optional[bool] = Query(None, description="Filter by system role status", alias="isSystemRole"),
    controller: RoleController = Depends(get_role_controller)
):
    """Get all roles with pagination, filtering and sorting."""
    return await controller.get_all_roles(
        page=page,
        page_size=page_size,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
        is_active=is_active,
        is_system_role=is_system_role
    )


@router.post("/system",
             responses={
                 400: {"description": "User or role not found"},
                 500: {"description": "Internal server error"}
             }, response_model=StandardResponse[None])
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
    return StandardResponse(message="Role assigned successfully", data=None)


@router.patch("/{role_id}", response_model=StandardResponse[RoleResponse],
              responses={
                  400: {"description": "Role not found"},
                  500: {"description": "Internal server error"}
})
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


@router.delete("/{role_id}", response_model=StandardResponse[RoleResponse],
               responses={
                   400: {"description": "Role not found"},
                   500: {"description": "Internal server error"}
})
async def delete_role(
    request: Request,
    role_id: int,
    controller: RoleController = Depends(get_role_controller)
):
    """Delete an existing role by marking it as inactive"""
    return await controller.delete_role(role_id)


@router.get("/projects/{project_id}", response_model=StandardResponse[PaginatedGetProjectRolesResponse],
            responses={
                404: {"description": "Project not found"},
                500: {"description": "Internal server error"}
})
async def get_project_roles(
    request: Request,
    project_id: int,
    page: int = Query(1, ge=1),
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
    return await controller.get_project_roles_by_project_id(
        project_id=project_id,
        page=page,
        page_size=page_size,
        role_name=role_name,
        search=search
    )


@router.post("/projects/{project_id}",
             responses={
                 400: {"description": "Project not found or invalid role assignments or user not found"},
                 500: {"description": "Internal server error"}
             }, response_model=StandardResponse[None])
async def assign_project_role(
    request: Request,
    project_id: int,
    assignment: AssignProjectRoleRequest,
    controller: RoleController = Depends(get_role_controller)
):
    """Assign or update role for a user in a project.

    Args:
        request: FastAPI request object
        project_id: ID of the project
        assignment: Role assignment
        controller: Role controller instance
    """
    await controller.assign_project_role(project_id, assignment)
    return StandardResponse(message="Role assigned successfully", data=None)


@router.get(
    "/all",
    response_model=StandardResponse[List[RoleResponse]],
    summary="Get all roles without pagination"
)
async def get_all_roles_without_pagination(
    request: Request,
    is_active: Optional[bool] = Query(None, description="Filter by active status", alias="isActive"),
    controller: RoleController = Depends(get_role_controller)
):
    """Get all roles without pagination.

    Args:
        request: FastAPI request object
        is_active: Optional filter by active status
        controller: Role controller instance

    Returns:
        List of all roles matching the active status filter
    """
    return await controller.get_all_roles_without_pagination(
        is_active=is_active
    )
