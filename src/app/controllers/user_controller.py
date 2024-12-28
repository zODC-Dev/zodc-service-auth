from fastapi import HTTPException

from src.app.schemas.responses.user import UserResponse
from src.app.services.user_service import UserService
from src.domain.exceptions.user_exceptions import UserNotFoundError


class UserController:
    def __init__(self, user_service: UserService):
        self.user_service = user_service

    async def get_me(self, user_id: int) -> UserResponse:
        try:
            user = await self.user_service.get_current_user(user_id)
            return UserResponse.from_domain(user)
        except UserNotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e)) from e
        except Exception as e:
            raise HTTPException(
                status_code=500, detail="Failed to get user information") from e
