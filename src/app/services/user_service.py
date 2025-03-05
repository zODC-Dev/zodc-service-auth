from datetime import timedelta
from typing import Any, Dict, List, Optional

from src.domain.entities.user import User
from src.domain.exceptions.user_exceptions import (
    UserInactiveError,
    UserNotFoundError,
)
from src.domain.repositories.user_repository import IUserRepository
from src.domain.services.redis_service import IRedisService


class UserService:
    def __init__(self, user_repository: IUserRepository, redis_service: IRedisService):
        self.user_repository = user_repository
        self.redis_service = redis_service
        self.cache_ttl = timedelta(minutes=5)

    async def get_current_user(self, user_id: int) -> User:
        """Get current user information with project roles and permissions"""
        cache_key = f"user:{user_id}"

        # Try to get from cache
        cached_user = await self.redis_service.get(cache_key)
        if cached_user:
            return User.model_validate(cached_user)

        # Get from database with project roles and permissions
        user = await self.user_repository.get_user_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"User with id {user_id} not found")
        if not user.is_active:
            raise UserInactiveError(f"User with id {user_id} is inactive")

        # Cache user data
        await self.redis_service.set(
            key=cache_key,
            value=user.model_dump(),
            expiry=int(self.cache_ttl.total_seconds())
        )
        return user

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        user = await self.user_repository.get_user_by_email(email)
        if not user:
            raise UserNotFoundError(f"User with email {email} not found")
        return user

    def _validate_update_data(self, update_data: Dict[str, Any]) -> bool:
        """Validate user update data"""
        allowed_fields = {"name", "email", "is_active"}
        return all(key in allowed_fields for key in update_data.keys())

    async def get_users_by_ids(self, user_ids: List[int]) -> List[User]:
        """Get multiple users by their IDs"""
        users = []
        for user_id in user_ids:
            try:
                user = await self.get_current_user(user_id)
                users.append(user)
            except Exception:
                # Skip users that can't be retrieved
                continue
        return users
