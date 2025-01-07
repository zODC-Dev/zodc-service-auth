from typing import TYPE_CHECKING, List, Optional

from sqlmodel import Field, Relationship

from .base import BaseModelWithTimestamps

if TYPE_CHECKING:
    from .role import Role

from .role_permission import RolePermission


class Permission(BaseModelWithTimestamps, table=True):
    __tablename__ = "permissions"

    name: str = Field(unique=True, index=True)
    description: Optional[str] = None
    group: Optional[str] = None

    # Use actual model class for link_model
    roles: List["Role"] = Relationship(
        back_populates="permissions",
        link_model=RolePermission,
        sa_relationship_kwargs={"lazy": "selectin",
                                "overlaps": "permission,role,role_permissions"}
    )

    role_permissions: List["RolePermission"] = Relationship(
        back_populates="permission",
        sa_relationship_kwargs={"lazy": "selectin",
                                "overlaps": "permissions,roles"}
    )
