from typing import TYPE_CHECKING, List, Optional

from sqlmodel import Field, Relationship

from .base import BaseModelWithTimestamps
from .user_project_role import UserProjectRole

if TYPE_CHECKING:
    from .user import User
    from .user_performance import UserPerformance


class Project(BaseModelWithTimestamps, table=True):
    __tablename__ = "projects"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=255)
    key: str = Field(max_length=10, unique=True)
    jira_project_id: Optional[str] = Field(default=None)
    description: Optional[str] = None
    avatar_url: Optional[str] = None

    # Relationships
    users: List["User"] = Relationship(
        back_populates="projects",
        link_model=UserProjectRole,
        sa_relationship_kwargs={
            "lazy": "selectin",
            "overlaps": "user,project,user_project_roles"
        }
    )
    user_project_roles: List["UserProjectRole"] = Relationship(
        back_populates="project",
        sa_relationship_kwargs={
            "lazy": "selectin",
            "overlaps": "users,projects"
        }
    )

    performance_records: List["UserPerformance"] = Relationship(
        back_populates="project",
        sa_relationship_kwargs={"lazy": "selectin"}
    )
