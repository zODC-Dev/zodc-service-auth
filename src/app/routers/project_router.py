from typing import List, Optional

from fastapi import APIRouter, Depends, Query, Request

from src.app.controllers.project_controller import ProjectController
from src.app.dependencies.auth import get_jwt_claims, require_auth
from src.app.dependencies.project import get_project_controller
from src.app.schemas.requests.auth import JWTClaims
from src.app.schemas.requests.project import LinkJiraProjectRequest, ProjectCreateRequest, ProjectUpdateRequest
from src.app.schemas.responses.base import StandardResponse
from src.app.schemas.responses.project import (
    PaginatedProjectUsersWithRolesResponse,
    ProjectAssigneeResponse,
    ProjectResponse,
)
from src.domain.constants.roles import SystemRoles

router = APIRouter()


@router.post("", response_model=StandardResponse[ProjectResponse])
async def create_project(
    request: Request,
    project_data: ProjectCreateRequest,
    controller: ProjectController = Depends(get_project_controller)
):
    """Create a new project."""
    return await controller.create_project(project_data)


@router.get("/{project_id}", response_model=StandardResponse[ProjectResponse])
async def get_project(
    request: Request,
    project_id: int,
    controller: ProjectController = Depends(get_project_controller)
):
    """Get a project by ID."""
    return await controller.get_project(project_id)


@router.get("", response_model=StandardResponse[List[ProjectResponse]])
async def get_all_projects(
    request: Request,
    controller: ProjectController = Depends(get_project_controller),
    auth_data=require_auth(
        system_roles=[SystemRoles.PRODUCT_OWNER]
    )
):
    """Get all projects."""
    return await controller.get_all_projects()


@router.put("/{project_id}", response_model=StandardResponse[ProjectResponse])
async def update_project(
    request: Request,
    project_id: int,
    project_data: ProjectUpdateRequest,
    controller: ProjectController = Depends(get_project_controller)
):
    """Update a project."""
    return await controller.update_project(project_id, project_data)


@router.delete("/{project_id}", response_model=StandardResponse[None])
async def delete_project(
    request: Request,
    project_id: int,
    controller: ProjectController = Depends(get_project_controller)
):
    """Delete a project."""
    await controller.delete_project(project_id)
    return StandardResponse(message="Project deleted successfully", data=None)


@router.get("/user/{user_id}", response_model=StandardResponse[List[ProjectResponse]])
async def get_user_projects(
    request: Request,
    user_id: int,
    controller: ProjectController = Depends(get_project_controller)
):
    """Get all projects for a specific user."""
    return await controller.get_user_projects(user_id)


@router.post("/jira/link", response_model=StandardResponse[ProjectResponse])
async def link_jira_project(
    request: LinkJiraProjectRequest,
    claims: JWTClaims = Depends(get_jwt_claims),
    controller: ProjectController = Depends(get_project_controller)
):
    """Link project with Jira project"""
    # TODO: Create user if not exists, is_active = False, is_jira_linked = False
    user_id = int(claims.sub)
    return await controller.link_jira_project(request, user_id)


@router.get(
    "/{project_id}/users/all",
    response_model=StandardResponse[List[ProjectAssigneeResponse]],
    summary="Get all users in a project with their roles"
)
async def get_project_assignees(
    request: Request,
    project_id: int,
    search: Optional[str] = None,
    controller: ProjectController = Depends(get_project_controller)
):
    """Get all users in a project with their roles.

    Args:
        request: FastAPI request object
        project_id: The ID of the project
        search: Optional search term to filter users by name or email
        controller: Project controller instance

    Returns:
        List of users with their roles in the project
    """
    return await controller.get_project_assignees(
        project_id=project_id,
        search=search
    )


@router.get(
    "/{project_id}/users",
    response_model=StandardResponse[PaginatedProjectUsersWithRolesResponse],
    summary="Get users in a project with their roles with pagination, filtering, searching, and sorting"
)
async def get_project_users_with_roles_paginated(
    request: Request,
    project_id: int,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page", alias="pageSize"),
    search: Optional[str] = Query(None, description="Search by user name or email"),
    sort_by: Optional[str] = Query(
        None, description="Field to sort by (name, email, role_id)", alias="sortBy"),
    sort_order: Optional[str] = Query(None, description="Sort order (asc or desc)", alias="sortOrder"),
    role_id: Optional[int] = Query(None, description="Filter by role ID", alias="roleId"),
    controller: ProjectController = Depends(get_project_controller)
):
    """Get users in a project with their roles with pagination, filtering, searching, and sorting.

    Args:
        request: FastAPI request object
        project_id: The ID of the project
        page: Page number (starts at 1)
        page_size: Number of items per page
        search: Optional search term to filter users by name or email
        sort_by: Field to sort by (name, email, role_id)
        sort_order: Sort order (asc or desc)
        role_id: Filter by role ID
        controller: Project controller instance

    Returns:
        Paginated list of users with their roles in the project
    """
    return await controller.get_project_users_with_roles_paginated(
        project_id=project_id,
        page=page,
        page_size=page_size,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
        role_id=role_id
    )
