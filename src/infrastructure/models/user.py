from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from pydantic import EmailStr
from sqlmodel import JSON, Field, Relationship, SQLModel

from .base import BaseModelWithTimestamps
from .user_project_role import UserProjectRole

if TYPE_CHECKING:
    from .project import Project
    from .role import Role
    from .user_performance import UserPerformance


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
    is_system_user: bool = Field(default=True)  # Default to True for users who log in
    avatar_url: Optional[str] = Field(default=None)  # User's avatar URL from Jira
    # System-wide role (e.g., HR, System Admin)
    role_id: Optional[int] = Field(default=None, foreign_key="roles.id")
    # Profile data for extended user information
    profile_data: Optional[Dict[str, Any]] = Field(default_factory=dict, sa_type=JSON)
    # Basic profile fields
    job_title: Optional[str] = Field(default=None)
    location: Optional[str] = Field(default=None)
    phone_number: Optional[str] = Field(default=None)
    joined_date: Optional[datetime] = Field(default=None)

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

    performance_records: List["UserPerformance"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"lazy": "selectin"}
    )
