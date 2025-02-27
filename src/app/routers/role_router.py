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
from src.app.schemas.responses.role import (
    PaginatedGetProjectRolesResponse,
    PaginatedGetSystemRolesResponse,
    RoleResponse,
)

router = APIRouter()


@router.post("", response_model=RoleResponse,
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


@router.get("/system", response_model=PaginatedGetSystemRolesResponse,
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


@router.get("", response_model=List[RoleResponse])
async def get_roles(
    request: Request,
    include_deleted: bool = Query(False, alias="includeDeleted"),
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


@router.post("/system",
             responses={
                 400: {"description": "User or role not found"},
                 500: {"description": "Internal server error"}
             })
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


@router.patch("/{role_id}", response_model=RoleResponse,
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


@router.delete("/{role_id}", response_model=RoleResponse,
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


@router.get("/projects/{project_id}", response_model=PaginatedGetProjectRolesResponse,
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
             })
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
    return {"message": "Role assigned successfully"}
