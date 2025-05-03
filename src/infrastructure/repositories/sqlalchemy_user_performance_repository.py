from typing import List, Optional

from sqlalchemy.orm import selectinload
from sqlmodel import and_, col, select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.domain.entities.user_performance import UserPerformance, UserPerformanceCreate, UserPerformanceUpdate
from src.domain.repositories.user_performance_repository import IUserPerformanceRepository
from src.infrastructure.models.project import Project as SQLModelProject
from src.infrastructure.models.user_performance import (
    UserPerformance as SQLModelUserPerformance,
)
from src.utils.sql import attr


class SQLAlchemyUserPerformanceRepository(IUserPerformanceRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, performance: UserPerformanceCreate) -> UserPerformance:
        """Create a new performance record for a user"""
        project_result = await self.session.exec(select(SQLModelProject).where(col(SQLModelProject.key) == performance.project_key))
        project = project_result.one_or_none()

        if project is None:
            raise ValueError(f"Project with key {performance.project_key} not found")

        db_performance = SQLModelUserPerformance(
            user_id=performance.user_id,
            project_id=project.id,
            quarter=performance.quarter,
            year=performance.year,
            completion_date=performance.completion_date,
            scores={
                "overall": performance.overall,
                "code_quality": performance.code_quality,
                "test_coverage": performance.test_coverage,
                "documentation": performance.documentation,
            },
            data={
                "feedback": performance.feedback,
                "strengths": performance.strengths,
                "areas_for_improvement": performance.areas_for_improvement,
            },
        )

        self.session.add(db_performance)
        await self.session.commit()
        await self.session.refresh(db_performance)

        return await self._to_domain(db_performance)

    async def get_by_id(self, id: int) -> Optional[UserPerformance]:
        """Get a performance record by ID"""
        stmt = (
            select(SQLModelUserPerformance)
            .where(col(SQLModelUserPerformance.id) == id)
            .options(
                selectinload(attr(SQLModelUserPerformance.user)),
                selectinload(attr(SQLModelUserPerformance.project))
            )
        )

        result = await self.session.exec(stmt)
        db_performance = result.one_or_none()

        if db_performance is None:
            return None

        return await self._to_domain(db_performance)

    async def get_by_user_id(
        self,
        user_id: int,
        quarter: Optional[int] = None,
        year: Optional[int] = None
    ) -> List[UserPerformance]:
        """Get all performance records for a user, optionally filtered by quarter and year"""
        # Build query conditions
        conditions = [col(SQLModelUserPerformance.user_id) == user_id]

        if quarter is not None:
            conditions.append(col(SQLModelUserPerformance.quarter) == quarter)

        if year is not None:
            conditions.append(col(SQLModelUserPerformance.year) == year)

        stmt = (
            select(SQLModelUserPerformance)
            .where(and_(*conditions))
            .options(
                selectinload(attr(SQLModelUserPerformance.project))
            )
        )

        result = await self.session.exec(stmt)
        db_performances = result.all()

        return [await self._to_domain(performance) for performance in db_performances]

    async def get_by_project_id(
        self,
        project_id: int,
        quarter: Optional[int] = None,
        year: Optional[int] = None
    ) -> List[UserPerformance]:
        """Get all performance records for a project, optionally filtered by quarter and year"""
        # Build query conditions
        conditions = [col(SQLModelUserPerformance.project_id) == project_id]

        if quarter is not None:
            conditions.append(col(SQLModelUserPerformance.quarter) == quarter)

        if year is not None:
            conditions.append(col(SQLModelUserPerformance.year) == year)

        stmt = (
            select(SQLModelUserPerformance)
            .where(and_(*conditions))
            .options(
                selectinload(attr(SQLModelUserPerformance.user)),
                selectinload(attr(SQLModelUserPerformance.project))
            )
        )

        result = await self.session.exec(stmt)
        db_performances = result.all()

        return [await self._to_domain(performance) for performance in db_performances]

    async def update(self, id: int, performance: UserPerformanceUpdate) -> Optional[UserPerformance]:
        """Update a performance record"""
        stmt = (
            select(SQLModelUserPerformance)
            .where(col(SQLModelUserPerformance.id) == id)
            .options(
                selectinload(attr(SQLModelUserPerformance.user)),
                selectinload(attr(SQLModelUserPerformance.project))
            )
        )

        result = await self.session.exec(stmt)
        db_performance = result.one_or_none()

        if db_performance is None:
            return None

        update_data = performance.model_dump(exclude_unset=True, by_alias=True)
        scores = {
            "overall": update_data.get("overall"),
            "code_quality": update_data.get("code_quality"),
            "test_coverage": update_data.get("test_coverage"),
            "documentation": update_data.get("documentation"),
        }
        data = {
            "feedback": update_data.get("feedback"),
            "strengths": update_data.get("strengths"),
            "areas_for_improvement": update_data.get("areas_for_improvement"),
        }

        db_performance.scores = {**db_performance.scores, **scores}
        db_performance.data = {**db_performance.data, **data}

        await self.session.commit()
        await self.session.refresh(db_performance)

        return await self._to_domain(db_performance)

    async def delete(self, id: int) -> bool:
        """Delete a performance record"""
        stmt = (
            select(SQLModelUserPerformance)
            .where(col(SQLModelUserPerformance.id) == id)
        )

        result = await self.session.exec(stmt)
        db_performance = result.one_or_none()

        if db_performance is None:
            return False

        await self.session.delete(db_performance)
        await self.session.commit()

        return True

    async def _to_domain(self, db_performance: SQLModelUserPerformance) -> UserPerformance:
        """Convert SQLModel entity to domain entity"""
        # Create domain entity
        performance = UserPerformance(
            id=db_performance.id,
            user_id=db_performance.user_id,
            project_id=db_performance.project_id,
            quarter=db_performance.quarter,
            year=db_performance.year,
            completion_date=db_performance.completion_date,
            scores=db_performance.scores,
            data=db_performance.data,
            created_at=db_performance.created_at,
            updated_at=db_performance.updated_at,
        )

        # Assign project if available
        if db_performance.project:
            from src.domain.entities.project import Project
            performance.project = Project(
                id=db_performance.project.id,
                name=db_performance.project.name,
                key=db_performance.project.key,
                description=db_performance.project.description,
                avatar_url=db_performance.project.avatar_url,
                created_at=db_performance.project.created_at,
                updated_at=db_performance.project.updated_at
            )

        return performance
