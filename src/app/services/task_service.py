from ..repositories.task_repository import task_repository
from ..schemas.task import TaskCreate, TaskUpdate
from sqlalchemy.ext.asyncio import AsyncSession

class TaskService:
    async def create_task(self, db: AsyncSession, task: TaskCreate):
        return await task_repository.create(db, task)

    async def get_task(self, db: AsyncSession, task_id: int):
        return await task_repository.get(db, task_id)

    async def get_tasks(self, db: AsyncSession, skip: int = 0, limit: int = 100):
        return await task_repository.get_all(db, skip, limit)

    async def update_task(self, db: AsyncSession, task_id: int, task: TaskUpdate):
        return await task_repository.update(db, task_id, task)

    async def delete_task(self, db: AsyncSession, task_id: int):
        return await task_repository.delete(db, task_id)

    async def mark_task_as_completed(self, db: AsyncSession, task_id: int):
        task = await task_repository.get(db, task_id)
        if task:
            task.is_completed = True
            return await task_repository.update(db, task_id, TaskUpdate(is_completed=True))
        return None

task_service = TaskService()