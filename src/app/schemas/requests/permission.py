from typing import List, Optional

from pydantic import BaseModel

from src.domain.entities.permission import PermissionVerificationPayload as DomainPermissionVerificationPayload


class PermissionVerificationRequest(BaseModel):
    token: str
    user_id: int
    permissions: List[str]
    project_id: Optional[int] = None
    scope: str = "system"  # "system" or "project"

    @classmethod
    def to_domain(cls, request: "PermissionVerificationRequest") -> DomainPermissionVerificationPayload:
        return DomainPermissionVerificationPayload(
            token=request.token,
            user_id=request.user_id,
            permissions=request.permissions,
            project_id=request.project_id,
            scope=request.scope
        )
