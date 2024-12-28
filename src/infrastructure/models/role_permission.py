from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .permission import Permission
    from .role import Role


class RolePermission(SQLModel, table=True):
    __tablename__ = "role_permissions"

    # id: Optional[int] = Field(default=None, primary_key=True,
    #                           index=True, sa_column_kwargs={"autoincrement": True})

    role_id: Optional[int] = Field(
        default=None,
        foreign_key="roles.id",
        primary_key=True
    )
    permission_id: Optional[int] = Field(
        default=None,
        foreign_key="permissions.id",
        primary_key=True
    )

    role: "Role" = Relationship(
        back_populates="role_permissions", sa_relationship_kwargs={"lazy": "selectin"})
    permission: "Permission" = Relationship(
        back_populates="role_permissions", sa_relationship_kwargs={"lazy": "selectin"})
