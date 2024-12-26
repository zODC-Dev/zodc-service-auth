from abc import ABC, abstractmethod
from typing import List, Optional

from src.domain.entities.permission import Permission
from src.domain.entities.role import Role, RoleCreate, RoleUpdate


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
    async def delete_role(self, role_id: int) -> None:
        pass

    @abstractmethod
    async def get_all_roles(self, include_deleted: bool = False) -> List[Role]:
        pass
