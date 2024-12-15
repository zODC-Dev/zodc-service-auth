from abc import ABC, abstractmethod
from typing import List, Optional

from ..entities.task import Task


class ITaskRepository(ABC):
    """Interface for task repository operations"""

    @abstractmethod
    async def create(self, task: Task) -> Task:
        """Create a new task"""
        pass

    @abstractmethod
    async def get(self, task_id: int) -> Optional[Task]:
        """Get task by ID"""
        pass

    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Task]:
        """Get all tasks with pagination"""
        pass

    @abstractmethod
    async def update(self, task: Task) -> Task:
        """Update existing task"""
        pass

    @abstractmethod
    async def delete(self, task_id: int) -> Optional[Task]:
        """Delete task by ID"""
        pass
