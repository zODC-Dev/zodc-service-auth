from typing import Any, Dict, Optional

from src.domain.entities.user import User
from src.domain.exceptions.user_exceptions import (
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

    def _validate_update_data(self, update_data: Dict[str, Any]) -> bool:
        """Validate user update data"""
        allowed_fields = {"full_name", "email", "is_active"}
        return all(key in allowed_fields for key in update_data.keys())
