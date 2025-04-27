from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, Optional

from pydantic import BaseModel, Field
from pydantic.alias_generators import to_camel

from .base import BaseEntity

if TYPE_CHECKING:
    from .project import Project
    from .user import User


class UserPerformance(BaseEntity):
    id: Optional[int] = None
    user_id: int
    project_id: Optional[int] = None
    quarter: int
    year: int
    completion_date: Optional[datetime] = None
    scores: Dict[str, Any]
    data: Dict[str, Any]
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None

    # Relationships
    user: Optional["User"] = None
    project: Optional["Project"] = None


class UserPerformanceCreate(BaseModel):
    user_id: int
    project_id: Optional[int] = None
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

    class Config:
        from_attributes = True
        populate_by_name = True
        alias_generator = to_camel


class UserPerformanceUpdate(BaseModel):
    quarter: Optional[int] = None
    year: Optional[int] = None
    completion_date: Optional[datetime] = None
    overall: Optional[float] = None
    code_quality: Optional[float] = None
    test_coverage: Optional[float] = None
    documentation: Optional[float] = None
    feedback: Optional[str] = None
    strengths: Optional[str] = None
    areas_for_improvement: Optional[str] = None

    class Config:
        from_attributes = True
        populate_by_name = True
        alias_generator = to_camel
