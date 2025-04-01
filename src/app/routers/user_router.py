from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.requests import Request

from src.app.controllers.project_controller import ProjectController
from src.app.controllers.user_controller import UserController
from src.app.dependencies.auth import CurrentUser
from src.app.dependencies.project import get_project_controller
from src.app.dependencies.user import get_user_controller
from src.app.schemas.responses.base import StandardResponse
from src.app.schemas.responses.project import ProjectAssigneeResponse, ProjectResponse
from src.app.schemas.responses.user import UserResponse
from src.app.utils.response_wrapper import wrap_response

router = APIRouter()


@router.get("/me", response_model=StandardResponse[UserResponse])
async def get_me(current_user: CurrentUser):
    """Get current user information"""
    user_response = UserResponse.from_domain(current_user)
    return wrap_response(data=user_response, message="User information retrieved successfully")


@router.get("/me/projects", response_model=StandardResponse[List[ProjectResponse]])
async def get_my_projects(
    current_user: CurrentUser,
    controller: ProjectController = Depends(get_project_controller)
):
    """Get all projects that the current user belongs to"""
    current_user_id = current_user.id
    if current_user_id is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return await controller.get_user_projects(current_user_id)


@router.get("/assignees", response_model=StandardResponse[List[ProjectAssigneeResponse]])
async def get_users(
    request: Request,
    project_key: Optional[str] = Query(
        None, description="Optional project key to filter users by project", alias="projectKey"),
    search: Optional[str] = Query(None, description="Search by user name or email"),
    user_controller: UserController = Depends(get_user_controller),
    project_controller: ProjectController = Depends(get_project_controller)
):
    """Get all users with their roles. If project_key is provided, returns only users from that project.

    Args:
        request: FastAPI request object
        project_key: Optional project key to filter users by project
        search: Optional search term to filter users by name or email
        user_controller: User controller instance
        project_controller: Project controller instance

    Returns:
        List of users with their roles
    """
    if project_key:
        return await project_controller.get_project_assignees(
            project_key=project_key,
            search=search
        )
    return await user_controller.get_users(
        search=search
    )
