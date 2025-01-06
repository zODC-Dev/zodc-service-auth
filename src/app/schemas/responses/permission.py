from typing import List, Optional, Set

from pydantic import BaseModel

from src.domain.entities.permission import (
    Permission,
    PermissionVerificationResult as DomainPermissionVerificationResult,
)


class PermissionResponse(BaseModel):
    id: Optional[int] = None
    name: str
    description: Optional[str] = None
    group: Optional[str] = None

    @classmethod
    def from_domain(cls, permission: Permission) -> "PermissionResponse":
        return cls(
            id=permission.id,
            name=permission.name,
            description=permission.description,
            group=permission.group
        )


class GroupedPermissionResponse(BaseModel):
    groups: Set[str]
    permissions: List[PermissionResponse]

    @classmethod
    def from_domain(cls, permissions: List[Permission]) -> "GroupedPermissionResponse":
        return cls(
            groups=set(
                {permission.group for permission in permissions if permission.group}),
            permissions=[PermissionResponse.from_domain(
                permission) for permission in permissions]
        )


class PermissionVerificationResponse(BaseModel):
    allowed: bool
    user_id: int
    permissions: List[str]
    scope: str
    project_id: Optional[int] = None
    error: Optional[str] = None

    @classmethod
    def from_domain(cls, result: DomainPermissionVerificationResult) -> "PermissionVerificationResponse":
        return cls(
            allowed=result.allowed,
            user_id=result.user_id,
            permissions=result.permissions,
            scope=result.scope,
            project_id=result.project_id,
            error=result.error
        )
