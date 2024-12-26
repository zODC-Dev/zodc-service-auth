from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

# Use ForwardRef for circular dependencies
if TYPE_CHECKING:
    from .project import Project
    from .role import Role
    from .user import User


class UserProjectRole(SQLModel, table=True):
    __tablename__ = "user_project_roles"

    id: Optional[int] = Field(default=None, primary_key=True)

    user_id: int = Field(foreign_key="users.id")
    project_id: int = Field(foreign_key="projects.id")
    role_id: int = Field(foreign_key="roles.id")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = Field(default=None)

    user: "User" = Relationship(
        back_populates="user_project_roles", sa_relationship_kwargs={"lazy": "selectin"})
    project: "Project" = Relationship(
        back_populates="user_project_roles", sa_relationship_kwargs={"lazy": "selectin"})
    role: "Role" = Relationship(
        back_populates="user_project_roles", sa_relationship_kwargs={"lazy": "selectin"})
