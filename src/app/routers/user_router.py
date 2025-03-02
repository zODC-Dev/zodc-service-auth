from fastapi import APIRouter

from src.app.dependencies.auth import CurrentUser
from src.app.schemas.responses.base import StandardResponse
from src.app.schemas.responses.user import UserResponse
from src.app.utils.response_wrapper import wrap_response

router = APIRouter()


@router.get("/me", response_model=StandardResponse[UserResponse])
async def get_me(current_user: CurrentUser):
    """Get current user information"""
    user_response = UserResponse.from_domain(current_user)
    return wrap_response(data=user_response, message="User information retrieved successfully")
