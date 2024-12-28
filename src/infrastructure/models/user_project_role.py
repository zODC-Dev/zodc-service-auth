from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship

from .base import BaseModelWithTimestamps

# Use ForwardRef for circular dependencies
if TYPE_CHECKING:
    from .project import Project
    from .role import Role
    from .user import User


class UserProjectRole(BaseModelWithTimestamps, table=True):
    __tablename__ = "user_project_roles"

    user_id: int = Field(foreign_key="users.id")
    project_id: int = Field(foreign_key="projects.id")
    role_id: int = Field(foreign_key="roles.id")

    user: "User" = Relationship(
        back_populates="user_project_roles", sa_relationship_kwargs={"lazy": "selectin"})
    project: "Project" = Relationship(
        back_populates="user_project_roles", sa_relationship_kwargs={"lazy": "selectin"})
    role: "Role" = Relationship(
        back_populates="user_project_roles", sa_relationship_kwargs={"lazy": "selectin"})
