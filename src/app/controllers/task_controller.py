from typing import List

from fastapi import HTTPException

from src.app.schemas.task import TaskCreate, TaskResponse, TaskUpdate
from src.app.services.task_service import TaskService
from src.domain.exceptions.task_exceptions import TaskDomainError, TaskNotFoundError


class TaskController:
    def __init__(self, task_service: TaskService):
        self.task_service = task_service

    async def create_task(self, task: TaskCreate) -> TaskResponse:
        try:
            created_task = await self.task_service.create_task(task)
            return TaskResponse.from_domain(created_task)
        except TaskDomainError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e

    async def get_task(self, task_id: int) -> TaskResponse:
        try:
            task = await self.task_service.get_task(task_id)
            return TaskResponse.from_domain(task)
        except TaskNotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e)) from e

    async def get_tasks(
        self, skip: int = 0, limit: int = 100
    ) -> List[TaskResponse]:
        tasks = await self.task_service.get_tasks(skip, limit)
        return [TaskResponse.from_domain(task) for task in tasks]

    async def update_task(
        self, task_id: int, task: TaskUpdate
    ) -> TaskResponse:
        try:
            updated_task = await self.task_service.update_task(task_id, task)
            return TaskResponse.from_domain(updated_task)
        except TaskNotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e)) from e
        except TaskDomainError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e

    async def delete_task(self, task_id: int) -> TaskResponse:
        try:
            task = await self.task_service.delete_task(task_id)
            return TaskResponse.from_domain(task)
        except TaskNotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e)) from e
