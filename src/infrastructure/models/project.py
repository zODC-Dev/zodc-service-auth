from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlmodel import Field, Relationship, SQLModel

from .user_project_role import UserProjectRole

if TYPE_CHECKING:
    from .user import User


class Project(SQLModel, table=True):
    __tablename__ = "projects"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)
    key: str = Field(unique=True, index=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = Field(default=None)
    description: Optional[str] = None

    # Relationship with users through UserProjectRole
    users: List["User"] = Relationship(
        back_populates="projects",
        link_model=UserProjectRole,
        sa_relationship_kwargs={
            "lazy": "selectin",
            "overlaps": "project_roles,user"
        }
    )

    user_project_roles: List["UserProjectRole"] = Relationship(
        back_populates="project",
        sa_relationship_kwargs={
            "lazy": "selectin",
            "overlaps": "users"
        }
    )
