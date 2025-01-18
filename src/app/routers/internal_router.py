from typing import Annotated

from fastapi import APIRouter, Depends

from src.app.controllers.internal_controller import InternalController
from src.app.dependencies.internal import get_internal_controller
from src.app.schemas.responses.internal import TokenResponse

router = APIRouter()


@router.get("/microsoft/token/{user_id}", response_model=TokenResponse)
async def get_microsoft_token(
    user_id: int,
    controller: Annotated[InternalController, Depends(get_internal_controller)]
):
    """Get valid Microsoft access token for a user"""
    return await controller.get_microsoft_token(user_id)


@router.get("/jira/token/{user_id}", response_model=TokenResponse)
async def get_jira_token(
    user_id: int,
    controller: Annotated[InternalController, Depends(get_internal_controller)]
):
    """Get valid Jira access token for a user"""
    return await controller.get_jira_token(user_id)
