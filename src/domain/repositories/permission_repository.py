from abc import ABC, abstractmethod
from typing import List

from src.domain.entities.permission import Permission
from src.domain.value_objects.permissions import ProjectPermission, SystemPermission


class IPermissionRepository(ABC):
    @abstractmethod
    async def get_all_permissions(self) -> List[Permission]:
        """Get all available permissions"""
        pass

    @abstractmethod
    async def get_permissions_by_names(self, permission_names: List[str]) -> List[Permission]:
        """Get permissions by their names"""
        pass

    @abstractmethod
    async def get_system_permissions_by_user_id(self, user_id: int) -> SystemPermission:
        """Get user's system permissions"""
        pass

    @abstractmethod
    async def get_permissions_of_all_projects_by_user_id(self, user_id: int) -> List[ProjectPermission]:
        """Get user's permissions of all projects"""
        pass

    @abstractmethod
    async def get_permissions_of_project_by_user_id(self, user_id: int, project_id: int) -> List[Permission]:
        """Get user's permissions of a project"""
        pass

    @abstractmethod
    async def get_permissions_by_ids(self, permission_ids: List[int]) -> List[Permission]:
        """Get permissions by their ids"""
        pass
