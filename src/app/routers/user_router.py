from typing import List

from fastapi import APIRouter, Depends, HTTPException

from src.app.controllers.project_controller import ProjectController
from src.app.dependencies.auth import CurrentUser
from src.app.dependencies.project import get_project_controller
from src.app.schemas.responses.base import StandardResponse
from src.app.schemas.responses.project import ProjectResponse
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
