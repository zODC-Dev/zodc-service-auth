from typing import List

from src.app.schemas.responses.base import StandardResponse
from src.app.schemas.responses.user import UserResponse
from src.app.services.user_service import UserService
from src.domain.exceptions.user_exceptions import UserNotFoundError


class InternalController:
    def __init__(self, user_service: UserService):
        self.user_service = user_service

    async def get_users_by_ids(self, user_ids: List[int]) -> StandardResponse[List[UserResponse]]:
        """Get users by list of IDs. This is an internal API for microservice."""
        users = []
        errors = []

        for user_id in user_ids:
            try:
                user = await self.user_service.get_current_user(user_id)
                users.append(UserResponse.from_domain(user))
            except UserNotFoundError as e:
                errors.append({"user_id": user_id, "error": str(e)})
            except Exception as e:
                errors.append({"user_id": user_id, "error": f"Unexpected error: {str(e)}"})

        return StandardResponse(
            message="Users retrieved successfully",
            data=users,
        )
