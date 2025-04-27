from abc import ABC, abstractmethod
from typing import List, Optional

from src.domain.entities.user_performance import UserPerformance, UserPerformanceCreate, UserPerformanceUpdate


class IUserPerformanceRepository(ABC):
    @abstractmethod
    async def create(self, performance: UserPerformanceCreate) -> UserPerformance:
        """Create a new performance record for a user"""
        pass

    @abstractmethod
    async def get_by_id(self, id: int) -> Optional[UserPerformance]:
        """Get a performance record by ID"""
        pass

    @abstractmethod
    async def get_by_user_id(self, user_id: int, quarter: Optional[int] = None, year: Optional[int] = None) -> List[UserPerformance]:
        """Get all performance records for a user, optionally filtered by quarter and year"""
        pass

    @abstractmethod
    async def get_by_project_id(self, project_id: int, quarter: Optional[int] = None, year: Optional[int] = None) -> List[UserPerformance]:
        """Get all performance records for a project, optionally filtered by quarter and year"""
        pass

    @abstractmethod
    async def update(self, id: int, performance: UserPerformanceUpdate) -> Optional[UserPerformance]:
        """Update a performance record"""
        pass

    @abstractmethod
    async def delete(self, id: int) -> bool:
        """Delete a performance record"""
        pass
