from abc import ABC, abstractmethod
from typing import List, Optional, Tuple

from src.domain.entities.permission import Permission
from src.domain.entities.role import Role, RoleCreate, RoleUpdate
from src.domain.entities.user_project_role import UserProjectRole


class IRoleRepository(ABC):
    @abstractmethod
    async def get_role_by_name(self, name: str) -> Optional[Role]:
        pass

    @abstractmethod
    async def get_role_permissions(self, role_id: int) -> List[Permission]:
        pass

    @abstractmethod
    async def get_user_system_role(self, user_id: int) -> Optional[Role]:
        pass

    @abstractmethod
    async def get_user_project_roles(
        self,
        user_id: int,
        project_id: Optional[int] = None
    ) -> List[Role]:
        pass

    @abstractmethod
    async def assign_system_role_to_user(
        self,
        user_id: int,
        role_name: str
    ) -> None:
        pass

    @abstractmethod
    async def assign_project_role_to_user(
        self,
        user_id: int,
        project_id: int,
        role_name: str
    ) -> None:
        pass

    @abstractmethod
    async def create_role(self, role_data: RoleCreate) -> Role:
        pass

    @abstractmethod
    async def update_role(self, role_id: int, role_data: RoleUpdate) -> Role:
        pass

    @abstractmethod
    async def delete_role(self, role_id: int) -> Role:
        pass

    @abstractmethod
    async def get_all_roles(self, include_deleted: bool = False) -> List[Role]:
        pass

    @abstractmethod
    async def get_project_roles_by_project_id(
        self,
        project_id: int,
        page: int = 1,
        page_size: int = 10,
        role_name: Optional[str] = None,
        search: Optional[str] = None
    ) -> Tuple[List[UserProjectRole], int]:
        """Get paginated and filtered user role assignments for a project"""
        pass

    @abstractmethod
    async def get_system_roles(
        self,
        page: int = 1,
        page_size: int = 10,
        search: Optional[str] = None,
        sort_by: Optional[str] = None,
        sort_order: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> Tuple[List[Role], int]:
        """Get paginated and filtered system roles"""
        pass
