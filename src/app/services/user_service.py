from datetime import timedelta
from typing import Any, Dict, List, Optional

from src.configs.logger import log
from src.domain.entities.user import User, UserProfileUpdate
from src.domain.entities.user_performance import UserPerformance, UserPerformanceCreate, UserPerformanceUpdate
from src.domain.entities.user_project_history import UserProjectHistory
from src.domain.exceptions.user_exceptions import (
    UserInactiveError,
    UserNotFoundError,
)
from src.domain.repositories.user_performance_repository import IUserPerformanceRepository
from src.domain.repositories.user_project_history_repository import IUserProjectHistoryRepository
from src.domain.repositories.user_repository import IUserRepository
from src.domain.services.redis_service import IRedisService


class UserService:
    def __init__(
        self,
        user_repository: IUserRepository,
        user_project_history_repository: IUserProjectHistoryRepository,
        user_performance_repository: IUserPerformanceRepository,
        redis_service: IRedisService
    ):
        self.user_repository = user_repository
        self.user_project_history_repository = user_project_history_repository
        self.user_performance_repository = user_performance_repository
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

    async def get_users(
        self,
        search: Optional[str] = None
    ) -> List[User]:
        """Get users with their roles

        Args:
            search: Optional search term to filter users by name or email

        Returns:
            List of User objects
        """
        # Get all users from system
        return await self.user_repository.get_all_users(search=search)

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

    async def get_user_with_profile_data(self, user_id: int) -> User:
        """Get user with complete profile data (including relationships)"""
        cache_key = f"user_profile:{user_id}"

        # Try to get from cache
        cached_user = await self.redis_service.get(cache_key)
        if cached_user:
            return User.model_validate(cached_user)

        # Get from database with all profile relationships
        user = await self.user_repository.get_user_profile(user_id)
        if not user:
            raise UserNotFoundError(f"User with id {user_id} not found")
        if not user.is_active:
            raise UserInactiveError(f"User with id {user_id} is inactive")

        # Cache user profile data
        await self.redis_service.set(
            key=cache_key,
            value=user.model_dump(),
            expiry=int(self.cache_ttl.total_seconds())
        )

        return user

    async def get_user_project_history(self, user_id: int) -> List[UserProjectHistory]:
        """Get user's project history"""
        # Check if user exists
        user = await self.user_repository.get_user_by_id(user_id)
        log.info(f"User: {user}")
        if not user:
            raise UserNotFoundError(f"User with id {user_id} not found")

        # Get project history
        raw_history = await self.user_project_history_repository.get_by_user_id(user_id)
        log.info(f"Raw history: {raw_history}")
        return raw_history

    async def get_user_performance(
        self,
        user_id: int,
        quarter: Optional[int] = None,
        year: Optional[int] = None
    ) -> List[UserPerformance]:
        """Get user's performance records, optionally filtered by quarter and year"""
        # Check if user exists
        user = await self.user_repository.get_user_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"User with id {user_id} not found")

        # Get performance records
        return await self.user_performance_repository.get_by_user_id(
            user_id,
            quarter=quarter,
            year=year
        )

    async def update_user_profile(self, user_id: int, profile_data: UserProfileUpdate) -> User:
        """Update a user's profile data"""
        # Check if user exists
        user = await self.user_repository.get_user_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"User with id {user_id} not found")

        # Update profile data
        updated_user = await self.user_repository.update_profile(user_id, profile_data)

        # Clear cache
        await self.redis_service.delete(f"user:{user_id}")
        await self.redis_service.delete(f"user_profile:{user_id}")

        return updated_user

    async def get_users_by_project_id(self, project_id: int) -> List[User]:
        """Get users by project id"""
        user_project_roles = await self.user_repository.get_users_by_project(project_id)

        users: List[User] = [
            upr.user for upr in user_project_roles if upr.user is not None
        ]
        return users

    async def create_user_performance(self, performance_data: UserPerformanceCreate) -> UserPerformance:
        """Create a new performance record for a user

        Args:
            performance_data: Performance data to create

        Returns:
            Created performance record
        """
        # Check if user exists
        user = await self.user_repository.get_user_by_id(performance_data.user_id)
        if not user:
            raise UserNotFoundError(f"User with id {performance_data.user_id} not found")

        # Create performance record
        return await self.user_performance_repository.create(performance_data)

    async def update_user_performance(self, performance_id: int, performance_data: UserPerformanceUpdate) -> Optional[UserPerformance]:
        """Update an existing performance record

        Args:
            performance_id: ID of the performance record to update
            performance_data: Updated performance data

        Returns:
            Updated performance record, or None if record not found
        """
        # Get existing performance record to verify it exists
        existing_performance = await self.user_performance_repository.get_by_id(performance_id)
        if not existing_performance:
            return None

        # Update performance record
        updated_performance = await self.user_performance_repository.update(performance_id, performance_data)

        return updated_performance
