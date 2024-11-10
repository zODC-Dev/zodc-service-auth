from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ..schemas.task import TaskCreate, TaskUpdate
from ..services.task_service import task_service

class TaskController:
    async def create_task(self, task: TaskCreate, db: AsyncSession):
        return await task_service.create_task(db=db, task=task)

    async def read_task(self, task_id: int, db: AsyncSession):
        db_task = await task_service.get_task(db, task_id=task_id)
        if db_task is None:
            raise HTTPException(status_code=404, detail="Task not found")
        return db_task

    async def read_tasks(self, skip: int, limit: int, db: AsyncSession):
        tasks = await task_service.get_tasks(db, skip=skip, limit=limit)
        return tasks

    async def update_task(self, task_id: int, task: TaskUpdate, db: AsyncSession):
        db_task = await task_service.update_task(db, task_id=task_id, task=task)
        if db_task is None:
            raise HTTPException(status_code=404, detail="Task not found")
        return db_task

    async def delete_task(self, task_id: int, db: AsyncSession):
        db_task = await task_service.delete_task(db, task_id=task_id)
        if db_task is None:
            raise HTTPException(status_code=404, detail="Task not found")
        return db_task

task_controller = TaskController()