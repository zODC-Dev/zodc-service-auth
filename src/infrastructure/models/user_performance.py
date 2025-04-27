from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, Optional

from sqlmodel import JSON, Field, Relationship

from .base import BaseModelWithTimestamps

if TYPE_CHECKING:
    from .project import Project
    from .user import User


class UserPerformance(BaseModelWithTimestamps, table=True):
    __tablename__ = "user_performance"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    project_id: Optional[int] = Field(default=None, foreign_key="projects.id")
    quarter: int = Field(ge=1, le=4)
    year: int
    completion_date: Optional[datetime] = Field(default=None)
    scores: Dict[str, Any] = Field(default_factory=dict, sa_type=JSON)
    data: Dict[str, Any] = Field(default_factory=dict, sa_type=JSON)

    # Relationships
    user: Optional["User"] = Relationship(
        back_populates="performance_records",
        sa_relationship_kwargs={"lazy": "selectin"}
    )
    project: Optional["Project"] = Relationship(
        back_populates="performance_records",
        sa_relationship_kwargs={"lazy": "selectin"}
    )
