from typing import List

from fastapi import APIRouter, Depends

from src.app.controllers.internal_controller import InternalController
from src.app.dependencies.internal import get_internal_controller
from src.app.schemas.requests.user import UserIdsRequest
from src.app.schemas.responses.base import StandardResponse
from src.app.schemas.responses.user import UserWithProfileResponse
from src.domain.entities.user import User

router = APIRouter()


@router.post("/users", response_model=StandardResponse[List[UserWithProfileResponse]])
async def get_users_by_ids(
    request: UserIdsRequest,
    controller: InternalController = Depends(get_internal_controller)
):
    """Get users by list of IDs. This is an internal API for microservice."""
    return await controller.get_users_by_ids(request.user_ids)


@router.get("/projects/{project_key}/users", response_model=StandardResponse[List[User]])
async def get_users_by_project_key(
    project_key: str,
    controller: InternalController = Depends(get_internal_controller)
):
    """Get users by project key. This is an internal API for microservice."""
    return await controller.get_users_by_project_key(project_key)
