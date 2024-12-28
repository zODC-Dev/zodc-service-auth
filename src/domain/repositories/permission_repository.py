from abc import ABC, abstractmethod
from typing import List

from src.domain.entities.permission import Permission


class IPermissionRepository(ABC):
    @abstractmethod
    async def get_all_permissions(self) -> List[Permission]:
        """Get all available permissions"""
        pass

    @abstractmethod
    async def get_permissions_by_names(self, permission_names: List[str]) -> List[Permission]:
        """Get permissions by their names"""
        pass
