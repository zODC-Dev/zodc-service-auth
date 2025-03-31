from abc import ABC, abstractmethod
from typing import List, Optional

from src.domain.entities.user import User, UserCreate, UserUpdate, UserWithPassword
from src.domain.entities.user_project_role import UserProjectRole


class IUserRepository(ABC):
    @abstractmethod
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        pass

    @abstractmethod
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        pass

    @abstractmethod
    async def get_user_with_password_by_email(self, email: str) -> Optional[UserWithPassword]:
        """Get user by email with password"""
        pass

    @abstractmethod
    async def get_user_by_id_with_role_permissions(self, user_id: int) -> Optional[User]:
        """Get user by ID with role permissions"""
        pass

    @abstractmethod
    async def update_user_by_id(self, user_id: int, user: UserUpdate) -> None:
        """Update user by ID"""
        pass

    @abstractmethod
    async def get_user_by_jira_account_id(self, jira_account_id: str) -> Optional[User]:
        """Get user by Jira account ID"""
        pass

    @abstractmethod
    async def create_user(self, user: UserCreate) -> User:
        """Create new user"""
        pass

    @abstractmethod
    async def get_users_by_project(
        self,
        project_id: int,
        search: Optional[str] = None
    ) -> List[UserProjectRole]:
        """Get all users in a specific project with their roles"""
        pass

    @abstractmethod
    async def get_all_users(
        self,
        search: Optional[str] = None
    ) -> List[User]:
        """Get all users in the system with their roles"""
        pass
