from abc import ABC, abstractmethod
from typing import List

from src.domain.entities.permission import Permission, PermissionVerificationPayload, PermissionVerificationResult


class IPermissionService(ABC):
    @abstractmethod
    async def get_all_permissions(self) -> List[Permission]:
        """Get all permissions"""
        pass

    @abstractmethod
    async def verify_permission(
        self,
        payload: PermissionVerificationPayload
    ) -> PermissionVerificationResult:
        """Verify if user has ALL permissions in given scope"""
        pass
