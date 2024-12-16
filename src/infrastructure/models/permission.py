from typing import TYPE_CHECKING, List, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .role import Role

from .role_permission import RolePermission


class Permission(SQLModel, table=True):
    __tablename__ = "permissions"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)
    description: Optional[str] = None

    # Use actual model class for link_model
    roles: List["Role"] = Relationship(
        back_populates="permissions",
        link_model=RolePermission,
        sa_relationship_kwargs={"lazy": "selectin"}
    )
