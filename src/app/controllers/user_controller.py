from typing import List, Optional

from fastapi import HTTPException

from src.app.schemas.responses.base import StandardResponse
from src.app.schemas.responses.project import ProjectAssigneeResponse
from src.app.schemas.responses.user import AdminUserResponse, UserResponse
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

    async def get_users(
        self,
        search: Optional[str] = None
    ) -> StandardResponse[List[ProjectAssigneeResponse]]:
        """Get all users with their roles.

        Args:
            project_id: Optional project ID to filter users by project
            search: Optional search term to filter users by name or email

        Returns:
            List of users with their roles
        """
        try:
            users = await self.user_service.get_users(
                search=search
            )

            return StandardResponse(
                message="Users retrieved successfully",
                data=[
                    ProjectAssigneeResponse.from_user(user)
                    for user in users
                ]
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to retrieve users: {str(e)}"
            ) from e

    async def get_users_for_admin(
        self,
        search: Optional[str] = None
    ) -> StandardResponse[List[AdminUserResponse]]:
        """Get all users with their roles.

        Args:
            project_id: Optional project ID to filter users by project
            search: Optional search term to filter users by name or email

        Returns:
            List of users with their roles
        """
        try:
            users = await self.user_service.get_users(
                search=search
            )

            return StandardResponse(
                message="Users retrieved successfully",
                data=[
                    AdminUserResponse.from_user(user)
                    for user in users
                ]
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to retrieve users: {str(e)}"
            ) from e
