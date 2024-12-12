from typing import List, Optional

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.domain.entities.task import Task
from src.domain.repositories.task_repository import ITaskRepository
from src.infrastructure.models.task import Task as TaskModel


class SQLAlchemyTaskRepository(ITaskRepository):
    """SQLAlchemy implementation of task repository"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, task: Task) -> Task:
        db_task = TaskModel(
            title=task.title,
            description=task.description,
            is_completed=task.is_completed
        )
        self.session.add(db_task)
        await self.session.commit()
        await self.session.refresh(db_task)
        return self._to_domain(db_task)

    async def get(self, task_id: int) -> Optional[Task]:
        result = await self.session.exec(
            select(TaskModel).where(TaskModel.id == task_id)
        )
        db_task = result.first()
        return self._to_domain(db_task) if db_task else None

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Task]:
        result = await self.session.exec(
            select(TaskModel).offset(skip).limit(limit)
        )
        return [self._to_domain(t) for t in result.all()]

    async def update(self, task: Task) -> Task:
        db_task = await self.session.get(TaskModel, task.id)
        if db_task:
            db_task.title = task.title
            db_task.description = task.description
            db_task.is_completed = task.is_completed
            db_task.updated_at = task.updated_at
            await self.session.commit()
            await self.session.refresh(db_task)
        return self._to_domain(db_task)

    async def delete(self, task_id: int) -> Optional[Task]:
        db_task = await self.session.get(TaskModel, task_id)
        if db_task:
            await self.session.delete(db_task)
            await self.session.commit()
            return self._to_domain(db_task)
        return None

    def _to_domain(self, db_task: TaskModel) -> Task:
        """Convert DB model to domain entity"""
        return Task(
            id=db_task.id,
            title=db_task.title,
            description=db_task.description,
            is_completed=db_task.is_completed,
            created_at=db_task.created_at,
            updated_at=db_task.updated_at
        )
