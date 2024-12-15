from typing import List

from src.app.schemas.task import TaskCreate, TaskUpdate
from src.domain.entities.task import Task
from src.domain.exceptions.task_exceptions import TaskNotFoundError
from src.domain.repositories.task_repository import ITaskRepository


class TaskService:
    """Application service for task operations"""

    def __init__(self, task_repository: ITaskRepository):
        self.task_repository = task_repository

    async def create_task(self, task_data: TaskCreate) -> Task:
        """Create a new task"""
        task = Task(
            title=task_data.title,
            description=task_data.description,
        )
        return await self.task_repository.create(task)

    async def get_task(self, task_id: int) -> Task:
        """Get task by ID"""
        task = await self.task_repository.get(task_id)
        if not task:
            raise TaskNotFoundError(f"Task with ID {task_id} not found")
        return task

    async def get_tasks(self, skip: int = 0, limit: int = 100) -> List[Task]:
        """Get all tasks with pagination"""
        return await self.task_repository.get_all(skip, limit)

    async def update_task(self, task_id: int, task_data: TaskUpdate) -> Task:
        """Update existing task"""
        task = await self.get_task(task_id)

        if task_data.title is not None:
            task.update_title(task_data.title)
        if task_data.description is not None:
            task.update_description(task_data.description)
        if task_data.is_completed is not None and task_data.is_completed:
            task.mark_as_completed()

        return await self.task_repository.update(task)

    async def delete_task(self, task_id: int) -> Task:
        """Delete task by ID"""
        task = await self.task_repository.delete(task_id)
        if not task:
            raise TaskNotFoundError(f"Task with ID {task_id} not found")
        return task
