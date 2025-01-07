from typing import TYPE_CHECKING, List, Optional

from sqlmodel import Field, Relationship

from .base import BaseModelWithTimestamps

if TYPE_CHECKING:
    from .permission import Permission
    from .user import User

from .role_permission import RolePermission
from .user_project_role import UserProjectRole


class Role(BaseModelWithTimestamps, table=True):
    __tablename__ = "roles"

    name: str = Field(unique=True, index=True)
    description: Optional[str] = None
    is_system_role: bool = Field(default=False)
    is_active: bool = Field(default=True)

    # Relationship with users (for system-wide roles)
    users: List["User"] = Relationship(
        back_populates="system_role",
        sa_relationship_kwargs={"lazy": "selectin"}
    )

    permissions: List["Permission"] = Relationship(
        back_populates="roles",
        link_model=RolePermission,
        sa_relationship_kwargs={"lazy": "selectin",
                                "overlaps": "role,permission"}
    )

    role_permissions: List["RolePermission"] = Relationship(
        back_populates="role",
        sa_relationship_kwargs={"lazy": "selectin",
                                "overlaps": "permissions"}
    )

    # Direct relationship with UserProjectRole entries
    user_project_roles: List["UserProjectRole"] = Relationship(
        back_populates="role",
        sa_relationship_kwargs={"lazy": "selectin"}
    )
