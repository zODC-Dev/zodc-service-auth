from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.requests import Request

from src.app.controllers.project_controller import ProjectController
from src.app.controllers.user_controller import UserController
from src.app.dependencies.auth import CurrentUser, get_jwt_claims
from src.app.dependencies.project import get_project_controller
from src.app.dependencies.user import get_user_controller
from src.app.schemas.requests.auth import JWTClaims
from src.app.schemas.requests.user import (
    CreateUserPerformanceRequest,
    UpdateUserPerformanceRequest,
    UpdateUserProfileRequest,
)
from src.app.schemas.responses.base import StandardResponse
from src.app.schemas.responses.performance import PerformanceResponse, ProjectPerformanceResponse
from src.app.schemas.responses.project import ProjectAssigneeResponse, ProjectResponse
from src.app.schemas.responses.user import AdminUserResponse, UserResponse, UserWithProfileResponse
from src.app.utils.response_wrapper import wrap_response

router = APIRouter()


@router.get("/me", response_model=StandardResponse[UserResponse])
async def get_me(current_user: CurrentUser):
    """Get current user information"""
    user_response = UserResponse.from_domain(current_user)
    return wrap_response(data=user_response, message="User information retrieved successfully")


@router.get("/me/profile", response_model=StandardResponse[UserWithProfileResponse])
async def get_my_profile(
    claims: JWTClaims = Depends(get_jwt_claims),
    user_controller: UserController = Depends(get_user_controller)
):
    """Get current user's complete profile information"""
    user_id = int(claims.sub)
    return await user_controller.get_me(user_id=user_id)


@router.put("/me/profile", response_model=StandardResponse[UserWithProfileResponse])
async def update_my_profile(
    request: UpdateUserProfileRequest,
    claims: JWTClaims = Depends(get_jwt_claims),
    user_controller: UserController = Depends(get_user_controller)
):
    """Update current user's profile information"""
    user_id = int(claims.sub)
    return await user_controller.update_my_profile(user_id, request)


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


@router.get("/me/performance", response_model=StandardResponse[List[ProjectPerformanceResponse]])
async def get_my_performance(
    current_user: CurrentUser,
    quarter: Optional[int] = Query(None, description="Filter by quarter (1-4)"),
    year: Optional[int] = Query(None, description="Filter by year"),
    user_controller: UserController = Depends(get_user_controller)
):
    """Get performance records for the current user"""
    current_user_id = current_user.id
    if current_user_id is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return await user_controller.get_user_performance_by_project(current_user_id, quarter=quarter, year=year)


@router.get("/{user_id}/performance", response_model=StandardResponse[List[ProjectPerformanceResponse]])
async def get_user_performance(
    user_id: int,
    quarter: Optional[int] = Query(None, description="Filter by quarter (1-4)"),
    year: Optional[int] = Query(None, description="Filter by year"),
    user_controller: UserController = Depends(get_user_controller)
):
    """Get performance records for a specific user"""
    return await user_controller.get_user_performance(user_id, quarter=quarter, year=year)


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


@router.get("/admin/all", response_model=StandardResponse[List[AdminUserResponse]])
async def get_users_for_admin(
    request: Request,
    search: Optional[str] = Query(None, description="Search by user name or email"),
    user_controller: UserController = Depends(get_user_controller),
):
    """Get all users with their roles. If project_key is provided, returns only users from that project.

    Args:
        request: FastAPI request object
        search: Optional search term to filter users by name or email
        user_controller: User controller instance

    Returns:
        List of users with their roles
    """
    return await user_controller.get_users_for_admin(
        search=search
    )


@router.get("/{user_id}/profile", response_model=StandardResponse[UserWithProfileResponse])
async def get_user_profile(
    user_id: int,
    user_controller: UserController = Depends(get_user_controller)
):
    """Get a user's complete profile information by ID (admin access)"""
    return await user_controller.get_user_profile(
        user_id
    )


@router.post("/{user_id}/performance", response_model=StandardResponse[PerformanceResponse])
async def create_user_performance(
    user_id: int,
    request: CreateUserPerformanceRequest,
    user_controller: UserController = Depends(get_user_controller)
):
    """Create a new performance record for a user

    Args:
        user_id: ID of the user to create performance for
        request: Performance data
        user_controller: User controller instance

    Returns:
        Created performance record
    """
    return await user_controller.create_user_performance(user_id, request)


@router.put("/performances/{performance_id}", response_model=StandardResponse[PerformanceResponse])
async def update_user_performance(
    performance_id: int,
    request: UpdateUserPerformanceRequest,
    user_controller: UserController = Depends(get_user_controller)
):
    """Update an existing performance record

    Args:
        performance_id: ID of the performance record to update
        request: Updated performance data
        user_controller: User controller instance

    Returns:
        Updated performance record
    """
    return await user_controller.update_user_performance(performance_id, request)
