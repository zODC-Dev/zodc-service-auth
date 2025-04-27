from typing import List, Optional

from sqlalchemy.orm import selectinload
from sqlmodel import col, select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.configs.logger import log
from src.domain.entities.user_project_history import (
    UserProjectHistory,
    UserProjectHistoryCreate,
    UserProjectHistoryUpdate,
)
from src.domain.repositories.user_project_history_repository import IUserProjectHistoryRepository
from src.infrastructure.models.user_project_history import (
    UserProjectHistory as SQLModelUserProjectHistory,
)
from src.utils.sql import attr


class SQLAlchemyUserProjectHistoryRepository(IUserProjectHistoryRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, project_history: UserProjectHistoryCreate) -> UserProjectHistory:
        """Create a new project history entry for a user"""
        db_project_history = SQLModelUserProjectHistory(
            user_id=project_history.user_id,
            project_id=project_history.project_id,
            data={
                "position": project_history.position,
                "start_date": project_history.start_date,
                "end_date": project_history.end_date,
                "description": project_history.description,
                "technologies": project_history.technologies
            }
        )

        self.session.add(db_project_history)
        await self.session.commit()
        await self.session.refresh(db_project_history)

        return await self._to_domain(db_project_history)

    async def get_by_id(self, id: int) -> Optional[UserProjectHistory]:
        """Get a project history entry by ID"""
        stmt = (
            select(SQLModelUserProjectHistory)
            .where(col(SQLModelUserProjectHistory.id) == id)
            .options(
                selectinload(attr(SQLModelUserProjectHistory.user)),
                selectinload(attr(SQLModelUserProjectHistory.project))
            )
        )

        result = await self.session.exec(stmt)
        db_history = result.one_or_none()

        if db_history is None:
            return None

        return await self._to_domain(db_history)

    async def get_by_user_id(self, user_id: int) -> List[UserProjectHistory]:
        """Get all project history entries for a user"""
        stmt = (
            select(SQLModelUserProjectHistory)
            .where(col(SQLModelUserProjectHistory.user_id) == user_id)
            # .options(
            # selectinload(attr(SQLModelUserProjectHistory.user), recursion_depth=1),
            # selectinload(attr(SQLModelUserProjectHistory.project), recursion_depth=1)
            # )
        )

        result = await self.session.exec(stmt)
        db_histories = result.all()

        return [await self._to_domain(history) for history in db_histories]

    async def get_by_project_id(self, project_id: int) -> List[UserProjectHistory]:
        """Get all project history entries for a project"""
        stmt = (
            select(SQLModelUserProjectHistory)
            .where(col(SQLModelUserProjectHistory.project_id) == project_id)
            .options(
                selectinload(attr(SQLModelUserProjectHistory.user)),
                selectinload(attr(SQLModelUserProjectHistory.project))
            )
        )

        result = await self.session.exec(stmt)
        db_histories = result.all()

        return [await self._to_domain(history) for history in db_histories]

    async def update(self, id: int, project_history: UserProjectHistoryUpdate) -> Optional[UserProjectHistory]:
        """Update a project history entry"""
        stmt = (
            select(SQLModelUserProjectHistory)
            .where(col(SQLModelUserProjectHistory.id) == id)
        )

        result = await self.session.exec(stmt)
        db_history = result.one_or_none()

        if db_history is None:
            return None

        update_data = project_history.model_dump(exclude_unset=True)
        db_history.data = {**db_history.data, **update_data}

        await self.session.commit()
        await self.session.refresh(db_history)

        return await self._to_domain(db_history)

    async def delete(self, id: int) -> bool:
        """Delete a project history entry"""
        stmt = (
            select(SQLModelUserProjectHistory)
            .where(col(SQLModelUserProjectHistory.id) == id)
        )

        result = await self.session.exec(stmt)
        db_history = result.one_or_none()

        if db_history is None:
            return False

        await self.session.delete(db_history)
        await self.session.commit()

        return True

    async def _to_domain(self, db_history: SQLModelUserProjectHistory) -> UserProjectHistory:
        """Convert SQLModel entity to domain entity"""
        log.info(f"Converting SQLModelUserProjectHistory to UserProjectHistory: {db_history}")
        # Create domain entity
        history = UserProjectHistory(
            id=db_history.id,
            user_id=db_history.user_id,
            project_id=db_history.project_id,
            data=db_history.data,
            created_at=db_history.created_at,
            updated_at=db_history.updated_at,
            # project=db_history.project,
            # user=db_history.user
        )

        return history
