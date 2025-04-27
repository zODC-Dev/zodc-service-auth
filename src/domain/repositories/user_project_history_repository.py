from abc import ABC, abstractmethod
from typing import List, Optional

from src.domain.entities.user_project_history import (
    UserProjectHistory,
    UserProjectHistoryCreate,
    UserProjectHistoryUpdate,
)


class IUserProjectHistoryRepository(ABC):
    @abstractmethod
    async def create(self, project_history: UserProjectHistoryCreate) -> UserProjectHistory:
        """Create a new project history entry for a user"""
        pass

    @abstractmethod
    async def get_by_id(self, id: int) -> Optional[UserProjectHistory]:
        """Get a project history entry by ID"""
        pass

    @abstractmethod
    async def get_by_user_id(self, user_id: int) -> List[UserProjectHistory]:
        """Get all project history entries for a user"""
        pass

    @abstractmethod
    async def get_by_project_id(self, project_id: int) -> List[UserProjectHistory]:
        """Get all project history entries for a project"""
        pass

    @abstractmethod
    async def update(self, id: int, project_history: UserProjectHistoryUpdate) -> Optional[UserProjectHistory]:
        """Update a project history entry"""
        pass

    @abstractmethod
    async def delete(self, id: int) -> bool:
        """Delete a project history entry"""
        pass
