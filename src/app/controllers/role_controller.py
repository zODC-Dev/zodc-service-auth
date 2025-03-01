from typing import Optional

from fastapi import HTTPException

from src.app.schemas.requests.role import (
    AssignProjectRoleRequest,
    AssignSystemRoleRequest,
    RoleCreateRequest,
    RoleUpdateRequest,
)
from src.app.schemas.responses.role import (
    GetProjectRoleResponse,
    GetSystemRoleResponse,
    PaginatedGetProjectRolesResponse,
    PaginatedGetSystemRolesResponse,
    PaginatedRoleResponse,
    RoleResponse,
)
from src.app.services.role_service import RoleService
from src.domain.exceptions.project_exceptions import ProjectNotFoundError
from src.domain.exceptions.role_exceptions import (
    RoleAlreadyExistsError,
    RoleError,
    RoleIsSystemRoleError,
    RoleNotFoundError,
)
from src.domain.exceptions.user_exceptions import UserNotFoundError


class RoleController:
    def __init__(self, role_service: RoleService):
        self.role_service = role_service

    async def create_role(self, role_data: RoleCreateRequest) -> RoleResponse:
        try:
            role = await self.role_service.create_role(role_data)
            return RoleResponse.from_domain(role)
        except RoleAlreadyExistsError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e
        except RoleError as e:
            raise HTTPException(status_code=500, detail=str(e)) from e

    async def update_role(self, role_id: int, role_data: RoleUpdateRequest) -> RoleResponse:
        try:
            role = await self.role_service.update_role(role_id, role_data)
            return RoleResponse.from_domain(role)
        except RoleNotFoundError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e
        except RoleError as e:
            raise HTTPException(status_code=500, detail=str(e)) from e

    async def get_all_roles(
        self,
        page: int = 1,
        page_size: int = 10,
        search: Optional[str] = None,
        sort_by: Optional[str] = None,
        sort_order: Optional[str] = None,
        is_active: Optional[bool] = None,
        is_system_role: Optional[bool] = None
    ) -> PaginatedRoleResponse:
        """Get paginated, filtered and sorted roles"""
        try:
            roles, total = await self.role_service.get_all_roles(
                page=page,
                page_size=page_size,
                search=search,
                sort_by=sort_by,
                sort_order=sort_order,
                is_active=is_active,
                is_system_role=is_system_role
            )

            return PaginatedRoleResponse(
                items=[RoleResponse.from_domain(role) for role in roles],
                total=total,
                page=page,
                page_size=page_size,
                total_pages=(total + page_size - 1) // page_size
            )
        except RoleError as e:
            raise HTTPException(status_code=500, detail=str(e)) from e

    async def delete_role(self, role_id: int) -> RoleResponse:
        try:
            deleted_role = await self.role_service.delete_role(role_id)
            return RoleResponse.from_domain(deleted_role)
        except RoleError as e:
            raise HTTPException(status_code=500, detail=str(e)) from e

    async def assign_system_role(self, request_data: AssignSystemRoleRequest) -> None:
        try:
            await self.role_service.assign_system_role(
                user_id=request_data.user_id,
                role_name=request_data.role_name
            )
        except (UserNotFoundError, RoleNotFoundError) as e:
            raise HTTPException(status_code=400, detail=str(e)) from e
        except RoleError as e:
            raise HTTPException(status_code=500, detail=str(e)) from e

    async def get_project_roles_by_project_id(
        self,
        project_id: int,
        page: int = 1,
        page_size: int = 10,
        role_name: Optional[str] = None,
        search: Optional[str] = None
    ) -> PaginatedGetProjectRolesResponse:
        try:
            user_project_roles, total = await self.role_service.get_project_roles_by_project_id(
                project_id=project_id,
                page=page,
                page_size=page_size,
                role_name=role_name,
                search=search
            )

            return PaginatedGetProjectRolesResponse(
                items=[GetProjectRoleResponse.from_domain(role)
                       for role in user_project_roles],
                total=total,
                page=page,
                page_size=page_size,
                total_pages=(total + page_size - 1) // page_size
            )
        except ProjectNotFoundError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e
        except RoleError as e:
            raise HTTPException(status_code=500, detail=str(e)) from e

    async def assign_project_role(self, project_id: int, assignment: AssignProjectRoleRequest) -> None:
        try:
            await self.role_service.assign_project_role(project_id, assignment)
        except (ProjectNotFoundError, RoleNotFoundError, UserNotFoundError, RoleIsSystemRoleError) as e:
            raise HTTPException(status_code=400, detail=str(e)) from e
        except RoleError as e:
            raise HTTPException(status_code=500, detail=str(e)) from e

    async def get_system_roles(
        self,
        page: int = 1,
        page_size: int = 10,
        search: Optional[str] = None,
        sort_by: Optional[str] = None,
        sort_order: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> PaginatedGetSystemRolesResponse:
        try:
            roles, total = await self.role_service.get_system_roles(
                page=page,
                page_size=page_size,
                search=search,
                sort_by=sort_by,
                sort_order=sort_order,
                is_active=is_active
            )

            return PaginatedGetSystemRolesResponse(
                items=[GetSystemRoleResponse.from_domain(
                    role) for role in roles],
                total=total,
                page=page,
                page_size=page_size,
                total_pages=(total + page_size - 1) // page_size
            )
        except RoleError as e:
            raise HTTPException(status_code=500, detail=str(e)) from e
