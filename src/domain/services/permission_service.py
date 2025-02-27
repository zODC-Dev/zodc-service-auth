from abc import ABC, abstractmethod
from typing import List

from src.domain.entities.permission import Permission


class IPermissionService(ABC):
    @abstractmethod
    async def get_all_permissions(self) -> List[Permission]:
        """Get all permissions"""
        pass
