from typing import TYPE_CHECKING, Any, Dict, Optional

from sqlmodel import JSON, Field, Relationship

from .base import BaseModelWithTimestamps

if TYPE_CHECKING:
    from .project import Project
    from .user import User


class UserProjectHistory(BaseModelWithTimestamps, table=True):
    __tablename__ = "user_project_history"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    project_id: int = Field(foreign_key="projects.id")
    data: Dict[str, Any] = Field(default_factory=dict, sa_type=JSON)

    # Relationships
    user: Optional["User"] = Relationship(
        back_populates="project_history",
        sa_relationship_kwargs={"lazy": "selectin"}
    )
    project: Optional["Project"] = Relationship(
        back_populates="user_history",
        sa_relationship_kwargs={"lazy": "selectin"}
    )
