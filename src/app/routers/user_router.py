from fastapi import APIRouter, Depends

from src.app.controllers.user_controller import UserController
from src.app.dependencies.auth import get_current_user
from src.app.dependencies.user import get_user_controller
from src.app.schemas.responses.user import UserResponse

router = APIRouter()

@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user_id: int = Depends(get_current_user),
    controller: UserController = Depends(get_user_controller)
):
    """Get current user information"""
    return await controller.get_me(current_user_id)
