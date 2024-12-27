from typing import List, Optional

from fastapi import HTTPException

from src.app.schemas.requests.role import (
    AssignProjectRoleRequest,
    AssignSystemRoleRequest,
    RoleCreateRequest,
    RoleUpdateRequest,
)
from src.app.schemas.responses.role import PaginatedUserRoleAssignmentResponse, RoleResponse
from src.app.services.role_service import RoleService
from src.domain.exceptions.project_exceptions import ProjectNotFoundError
from src.domain.exceptions.role_exceptions import RoleError


class RoleController:
    def __init__(self, role_service: RoleService):
        self.role_service = role_service

    async def create_role(self, role_data: RoleCreateRequest) -> RoleResponse:
        try:
            role = await self.role_service.create_role(role_data)
            return RoleResponse.from_domain(role)
        except RoleError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e

    async def update_role(self, role_id: int, role_data: RoleUpdateRequest) -> RoleResponse:
        try:
            role = await self.role_service.update_role(role_id, role_data)
            return RoleResponse.from_domain(role)
        except RoleError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e

    async def get_roles(self, include_deleted: bool = False) -> List[RoleResponse]:
        roles = await self.role_service.get_all_roles(include_deleted)
        return [RoleResponse.from_domain(role) for role in roles]

    async def assign_system_role(self, request_data: AssignSystemRoleRequest) -> None:
        try:
            await self.role_service.assign_system_role(
                user_id=request_data.user_id,
                role_name=request_data.role_name
            )
        except RoleError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e

    async def get_project_role_assignments(
        self,
        project_id: int,
        page: int = 1,
        page_size: int = 10,
        role_name: Optional[str] = None,
        search: Optional[str] = None
    ) -> PaginatedUserRoleAssignmentResponse:
        try:
            result = await self.role_service.get_project_role_assignments(
                project_id=project_id,
                page=page,
                page_size=page_size,
                role_name=role_name,
                search=search
            )

            return PaginatedUserRoleAssignmentResponse(
                items=result.items,
                total=result.total,
                page=result.page,
                page_size=result.page_size,
                total_pages=result.total_pages
            )
        except ProjectNotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e)) from e
        except RoleError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e

    async def assign_project_roles(self, project_id: int, assignments: List[AssignProjectRoleRequest]) -> None:
        try:
            await self.role_service.assign_project_roles(project_id, assignments)
        except ProjectNotFoundError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e
        except RoleError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e
