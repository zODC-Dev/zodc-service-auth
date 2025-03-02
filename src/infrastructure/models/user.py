from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from pydantic import EmailStr
from sqlmodel import JSON, Field, Relationship, SQLModel

from .base import BaseModelWithTimestamps
from .user_project_role import UserProjectRole

if TYPE_CHECKING:
    from .project import Project
    from .role import Role


class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True)
    name: str = Field(max_length=255)
    is_active: bool = Field(default=True)
    roles: List[str] = Field(default=["user"], sa_type=JSON)
    permissions: List[str] = Field(default_factory=list, sa_type=JSON)


class User(BaseModelWithTimestamps, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    name: str
    jira_account_id: Optional[str] = Field(default=None)
    password: Optional[str] = Field(default=None, max_length=60)
    is_active: bool = Field(default=True)
    is_jira_linked: bool = Field(default=False)
    # System-wide role (e.g., HR, System Admin)
    role_id: Optional[int] = Field(default=None, foreign_key="roles.id")

    # Relationships
    system_role: Optional["Role"] = Relationship(
        back_populates="users",
        sa_relationship_kwargs={"lazy": "selectin"}
    )
    projects: List["Project"] = Relationship(
        back_populates="users",
        link_model=UserProjectRole,
        sa_relationship_kwargs={
            "lazy": "selectin",
            "overlaps": "project,user,user_project_roles"
        }
    )
    user_project_roles: List["UserProjectRole"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={
            "lazy": "selectin",
            "overlaps": "projects,users"
        }
    )


class UserCreate(SQLModel):
    email: str = Field(unique=True, index=True)
    name: str
    is_active: bool = Field(default=True)
    jira_account_id: Optional[str] = Field(default=None)
    is_jira_linked: bool = Field(default=False)


class UserCreateSSO(UserBase):
    microsoft_id: str


class UserRead(UserBase):
    id: int
    created_at: datetime
    microsoft_id: Optional[str] = None


class UserUpdate(SQLModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None
    is_jira_linked: Optional[bool] = None
