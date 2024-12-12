from typing import List, Optional

from src.domain.entities.user import User
from src.domain.exceptions.user_exceptions import (
    InvalidUserDataError,
    UserInactiveError,
    UserNotFoundError,
)
from src.domain.repositories.user_repository import IUserRepository


class UserService:
    def __init__(self, user_repository: IUserRepository):
        self.user_repository = user_repository

    async def get_current_user(self, user_id: int) -> User:
        """Get current user information"""
        user = await self.user_repository.get_user_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"User with id {user_id} not found")
        if not user.is_active:
            raise UserInactiveError(f"User with id {user_id} is inactive")
        return user

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        user = await self.user_repository.get_user_by_email(email)
        if not user:
            raise UserNotFoundError(f"User with email {email} not found")
        return user


    async def update_user(self, user_id: int, update_data: dict) -> User:
        """Update user information"""
        # First get the user to ensure they exist
        user = await self.get_current_user(user_id)

        # Validate user
        if not user:
            raise UserNotFoundError("User not found")

        # Validate update data
        if not self._validate_update_data(update_data):
            raise InvalidUserDataError("Invalid update data provided")

        # Perform update
        updated_user = await self.user_repository.update_user(user_id, update_data)
        return updated_user

    async def update_user_roles(self, user_id: int, roles: List[str]) -> User:
        """Update user roles"""
        user = await self.get_current_user(user_id)

        if not user:
            raise UserNotFoundError("User not found")

        updated_user = await self.user_repository.update_user_roles(user_id, roles)
        return updated_user


    async def deactivate_user(self, user_id: int) -> User:
        """Deactivate a user"""
        user = await self.get_current_user(user_id)

        if not user:
            raise UserNotFoundError("User not found")
        deactivated_user = await self.user_repository.update_user(
            user_id,
            {"is_active": False}
        )
        return deactivated_user

    async def activate_user(self, user_id: int) -> User:
        """Activate a user"""
        # Here we don't use get_current_user as it checks for active status
        user = await self.user_repository.get_user_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"User with id {user_id} not found")

        activated_user = await self.user_repository.update_user(
            user_id,
            {"is_active": True}
        )
        return activated_user

    def _validate_update_data(self, update_data: dict) -> bool:
        """Validate user update data"""
        allowed_fields = {"full_name", "email", "is_active"}
        return all(key in allowed_fields for key in update_data.keys())
