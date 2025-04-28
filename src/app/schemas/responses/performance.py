from datetime import datetime
from typing import List, Optional

from src.app.schemas.responses.base import BaseResponse
from src.domain.entities.user_performance import UserPerformance


class PerformanceResponse(BaseResponse):
    id: int
    user_id: int
    project_id: Optional[int] = None
    project_name: Optional[str] = None
    project_key: Optional[str] = None
    quarter: int
    year: int
    completion_date: Optional[datetime] = None
    overall: float
    code_quality: Optional[float] = None
    test_coverage: Optional[float] = None
    documentation: Optional[float] = None
    feedback: Optional[str] = None
    strengths: Optional[str] = None
    areas_for_improvement: Optional[str] = None
    professional_summary: Optional[str] = None

    @classmethod
    def from_domain(cls, performance: UserPerformance) -> "PerformanceResponse":
        # Extract ratings
        scores_data = performance.scores or {}

        # Extract feedback
        data = performance.data or {}
        strengths = data.get("strengths", "")
        areas_for_improvement = data.get("areas_for_improvement", "")
        feedback = data.get("feedback", "")
        professional_summary = data.get("professional_summary", "")
        return cls(
            id=performance.id,
            user_id=performance.user_id,
            project_id=performance.project_id,
            project_name=performance.project.name if performance.project else None,
            project_key=performance.project.key if performance.project else None,
            quarter=performance.quarter,
            year=performance.year,
            completion_date=performance.completion_date,
            overall=scores_data.get("overall", 0.0),
            code_quality=scores_data.get("code_quality"),
            test_coverage=scores_data.get("test_coverage"),
            documentation=scores_data.get("documentation"),
            feedback=feedback,
            strengths=strengths,
            areas_for_improvement=areas_for_improvement,
            professional_summary=professional_summary,
        )


class ProjectPerformanceResponse(BaseResponse):
    """Response schema for performance grouped by project"""
    project_id: int
    project_name: str
    project_key: str
    performances: List[PerformanceResponse]

    @classmethod
    def from_performances(cls, project_id: int, project_name: str, project_key: str, performances: List[UserPerformance]) -> "ProjectPerformanceResponse":
        """Create a project performance response from a list of performances for the same project"""
        return cls(
            project_id=project_id,
            project_name=project_name,
            project_key=project_key,
            performances=[PerformanceResponse.from_domain(p) for p in performances]
        )
