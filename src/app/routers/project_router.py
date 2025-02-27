from typing import List

from fastapi import APIRouter, Depends, Request

from src.app.controllers.project_controller import ProjectController
from src.app.dependencies.auth import get_jwt_claims, require_auth
from src.app.dependencies.project import get_project_controller
from src.app.schemas.requests.auth import JWTClaims
from src.app.schemas.requests.project import LinkJiraProjectRequest, ProjectCreateRequest, ProjectUpdateRequest
from src.app.schemas.responses.project import ProjectResponse
from src.domain.constants.roles import SystemRoles

router = APIRouter()


@router.post("/", response_model=ProjectResponse)
async def create_project(
    request: Request,
    project_data: ProjectCreateRequest,
    controller: ProjectController = Depends(get_project_controller)
):
    """Create a new project."""
    return await controller.create_project(project_data)


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    request: Request,
    project_id: int,
    controller: ProjectController = Depends(get_project_controller)
):
    """Get a project by ID."""
    return await controller.get_project(project_id)


@router.get("/", response_model=List[ProjectResponse])
async def get_all_projects(
    request: Request,
    controller: ProjectController = Depends(get_project_controller),
    auth_data=require_auth(
        system_roles=[SystemRoles.USER]
    )
):
    """Get all projects."""
    return await controller.get_all_projects()


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    request: Request,
    project_id: int,
    project_data: ProjectUpdateRequest,
    controller: ProjectController = Depends(get_project_controller)
):
    """Update a project."""
    return await controller.update_project(project_id, project_data)


@router.delete("/{project_id}")
async def delete_project(
    request: Request,
    project_id: int,
    controller: ProjectController = Depends(get_project_controller)
):
    """Delete a project."""
    await controller.delete_project(project_id)
    return {"message": "Project deleted successfully"}


@router.get("/user/{user_id}", response_model=List[ProjectResponse])
async def get_user_projects(
    request: Request,
    user_id: int,
    controller: ProjectController = Depends(get_project_controller)
):
    """Get all projects for a specific user."""
    return await controller.get_user_projects(user_id)


@router.post("/jira/link", response_model=ProjectResponse)
async def link_jira_project(
    request: LinkJiraProjectRequest,
    claims: JWTClaims = Depends(get_jwt_claims),
    controller: ProjectController = Depends(get_project_controller)
):
    """Link project with Jira project"""
    # TODO: Create user if not exists, is_active = False, is_jira_linked = False
    user_id = int(claims.sub)
    return await controller.link_jira_project(request, user_id)
