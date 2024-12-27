from typing import List

from fastapi import APIRouter, Depends, Request

from src.app.controllers.project_controller import ProjectController
from src.app.decorators.auth_decorator import require_permissions
from src.app.dependencies.project import get_project_controller
from src.app.schemas.requests.project import ProjectCreateRequest, ProjectUpdateRequest
from src.app.schemas.responses.project import ProjectResponse

router = APIRouter()


@router.post("/", response_model=ProjectResponse)
@require_permissions(
    system_roles=["user"],
    # system_roles=["admin"],
    # permissions=["projects.manage"]
)
async def create_project(
    request: Request,
    project_data: ProjectCreateRequest,
    controller: ProjectController = Depends(get_project_controller)
):
    """Create a new project."""
    return await controller.create_project(project_data)


@router.get("/{project_id}", response_model=ProjectResponse)
@require_permissions(
    system_roles=["user"],
)
async def get_project(
    request: Request,
    project_id: int,
    controller: ProjectController = Depends(get_project_controller)
):
    """Get a project by ID."""
    return await controller.get_project(project_id)


@router.get("/", response_model=List[ProjectResponse])
# @require_permissions(system_roles=["user"])
async def get_all_projects(
    request: Request,
    controller: ProjectController = Depends(get_project_controller)
):
    """Get all projects."""
    return await controller.get_all_projects()


@router.put("/{project_id}", response_model=ProjectResponse)
@require_permissions(system_roles=["admin"])
async def update_project(
    request: Request,
    project_id: int,
    project_data: ProjectUpdateRequest,
    controller: ProjectController = Depends(get_project_controller)
):
    """Update a project."""
    return await controller.update_project(project_id, project_data)


@router.delete("/{project_id}")
@require_permissions(system_roles=["admin"])
async def delete_project(
    request: Request,
    project_id: int,
    controller: ProjectController = Depends(get_project_controller)
):
    """Delete a project."""
    await controller.delete_project(project_id)
    return {"message": "Project deleted successfully"}


@router.get("/user/{user_id}", response_model=List[ProjectResponse])
@require_permissions(system_roles=["user"])
async def get_user_projects(
    request: Request,
    user_id: int,
    controller: ProjectController = Depends(get_project_controller)
):
    """Get all projects for a specific user."""
    return await controller.get_user_projects(user_id)
