from datetime import datetime
from typing import List, Optional

from src.app.schemas.responses.base import BaseResponse
from src.app.schemas.responses.common import PaginatedResponse
from src.app.schemas.responses.permission import PermissionResponse
from src.domain.entities.role import Role
from src.domain.entities.user_project_role import UserProjectRole


class RoleResponse(BaseResponse):
    id: int
    name: str
    description: Optional[str]
    is_system_role: bool
    is_active: bool
    permission_names: List[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    @classmethod
    def from_domain(cls, role: Role) -> 'RoleResponse':
        return cls(
            id=role.id,
            name=role.name,
            description=role.description,
            is_system_role=role.is_system_role,
            is_active=role.is_active,
            permission_names=[
                p.name for p in role.permissions] if role.permissions else [],
            created_at=role.created_at,
            updated_at=role.updated_at
        )


class AdminRoleResponse(BaseResponse):
    id: int
    name: str
    description: Optional[str]
    is_system_role: bool
    is_active: bool
    permissions: List['PermissionResponse']
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    @classmethod
    def from_domain(cls, role: Role) -> 'AdminRoleResponse':
        return cls(
            id=role.id,
            name=role.name,
            description=role.description,
            is_system_role=role.is_system_role,
            is_active=role.is_active,
            permissions=[PermissionResponse.from_domain(p) for p in role.permissions] if role.permissions else [],
            created_at=role.created_at,
            updated_at=role.updated_at
        )


class GetProjectRoleResponse(BaseResponse):
    user_id: int
    user_name: str
    user_email: str
    role_name: Optional[str] = None

    @classmethod
    def from_domain(cls, assignment: UserProjectRole) -> 'GetProjectRoleResponse':
        return cls(
            user_id=assignment.user.id if assignment.user else None,
            user_name=assignment.user.name if assignment.user else None,
            user_email=assignment.user.email if assignment.user else None,
            role_name=assignment.role.name if assignment.role else None
        )

    class Config:
        from_attributes = True


class PaginatedGetProjectRolesResponse(PaginatedResponse[GetProjectRoleResponse]):
    pass


class GetSystemRoleResponse(BaseResponse):
    id: int
    name: str
    description: Optional[str]
    permissions: List[str]
    is_active: bool

    @classmethod
    def from_domain(cls, role: Role) -> 'GetSystemRoleResponse':
        return cls(
            id=role.id,
            name=role.name,
            description=role.description,
            permissions=[
                p.name for p in role.permissions] if role.permissions else [],
            is_active=role.is_active
        )


class PaginatedGetSystemRolesResponse(PaginatedResponse[GetSystemRoleResponse]):
    pass


class PaginatedRoleResponse(PaginatedResponse[RoleResponse]):
    pass
