from fastapi import APIRouter

from src.app.dependencies.auth import CurrentUser
from src.app.schemas.responses.user import UserResponse

router = APIRouter()

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: CurrentUser):
    """Get current user information"""
    return UserResponse.from_domain(current_user)
