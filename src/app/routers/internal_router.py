from typing import List

from fastapi import APIRouter, Depends

from src.app.controllers.internal_controller import InternalController
from src.app.dependencies.internal import get_internal_controller
from src.app.schemas.requests.user import UserIdsRequest
from src.app.schemas.responses.base import StandardResponse
from src.app.schemas.responses.user import UserResponse

router = APIRouter()


@router.post("/users", response_model=StandardResponse[List[UserResponse]])
async def get_users_by_ids(
    request: UserIdsRequest,
    controller: InternalController = Depends(get_internal_controller)
):
    """Get users by list of IDs. This is an internal API for microservice."""
    return await controller.get_users_by_ids(request.user_ids)
