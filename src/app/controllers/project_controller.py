from typing import List, Optional

from fastapi import HTTPException

from src.app.schemas.requests.project import LinkJiraProjectRequest, ProjectCreateRequest, ProjectUpdateRequest
from src.app.schemas.responses.project import (
    PaginatedProjectUsersWithRolesResponse,
    ProjectResponse,
    ProjectUsersWithRolesResponse,
    ProjectUserWithRoleResponse,
)
from src.app.services.project_service import ProjectService
from src.domain.entities.project import ProjectCreate, ProjectUpdate
from src.domain.exceptions.project_exceptions import ProjectError, UnauthorizedError


class ProjectController:
    def __init__(self, project_service: ProjectService):
        self.project_service = project_service

    async def create_project(self, project_data: ProjectCreateRequest) -> ProjectResponse:
        try:
            project = await self.project_service.create_project(
                ProjectCreate(
                    name=project_data.name,
                    key=project_data.key,
                    description=project_data.description
                )
            )
            return ProjectResponse.from_domain(project)
        except ProjectError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e

    async def get_project(self, project_id: int) -> ProjectResponse:
        try:
            project = await self.project_service.get_project(project_id)
            return ProjectResponse.from_domain(project)
        except ProjectError as e:
            raise HTTPException(status_code=404, detail=str(e)) from e

    async def get_all_projects(self) -> List[ProjectResponse]:
        projects = await self.project_service.get_all_projects()
        return [ProjectResponse.from_domain(p) for p in projects]

    async def update_project(
        self,
        project_id: int,
        project_data: ProjectUpdateRequest
    ) -> ProjectResponse:
        try:
            project = await self.project_service.update_project(
                project_id,
                ProjectUpdate(
                    key=project_data.key,
                    description=project_data.description
                )
            )
            return ProjectResponse.from_domain(project)
        except ProjectError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e

    async def delete_project(self, project_id: int) -> None:
        try:
            await self.project_service.delete_project(project_id)
        except ProjectError as e:
            raise HTTPException(status_code=404, detail=str(e)) from e

    async def get_user_projects(self, user_id: int) -> List[ProjectResponse]:
        projects = await self.project_service.get_user_projects(user_id)
        return [ProjectResponse.from_domain(p) for p in projects]

    async def link_jira_project(
        self,
        request: LinkJiraProjectRequest,
        current_user_id: int
    ) -> ProjectResponse:
        try:
            project = await self.project_service.link_jira_project(
                project_data=request,
                current_user_id=current_user_id
            )
            return ProjectResponse.from_domain(project)
        except (ProjectError, UnauthorizedError) as e:
            raise HTTPException(status_code=400, detail=str(e)) from e

    async def get_project_users_with_roles(
        self,
        project_id: int,
        search: Optional[str] = None
    ) -> ProjectUsersWithRolesResponse:
        """Get all users in a project with their roles

        Args:
            project_id: The ID of the project
            search: Optional search term to filter users by name or email

        Returns:
            List of users with their roles in the project
        """
        try:
            user_project_roles = await self.project_service.get_project_users_with_roles(
                project_id=project_id,
                search=search
            )
            return ProjectUsersWithRolesResponse.from_domain(user_project_roles)
        except ProjectError as e:
            raise HTTPException(status_code=404, detail=str(e)) from e

    async def get_project_users_with_roles_paginated(
        self,
        project_id: int,
        page: int = 1,
        page_size: int = 10,
        search: Optional[str] = None,
        sort_by: Optional[str] = None,
        sort_order: Optional[str] = None,
        role_name: Optional[str] = None
    ) -> PaginatedProjectUsersWithRolesResponse:
        """Get users in a project with their roles with pagination, filtering, searching, and sorting

        Args:
            project_id: The ID of the project
            page: Page number (starts at 1)
            page_size: Number of items per page
            search: Optional search term to filter users by name or email
            sort_by: Field to sort by (name, email, role_name)
            sort_order: Sort order (asc or desc)
            role_name: Filter by role name

        Returns:
            Paginated list of users with their roles in the project
        """
        try:
            user_project_roles, total = await self.project_service.get_project_users_with_roles_paginated(
                project_id=project_id,
                page=page,
                page_size=page_size,
                search=search,
                sort_by=sort_by,
                sort_order=sort_order,
                role_name=role_name
            )

            return PaginatedProjectUsersWithRolesResponse(
                items=[ProjectUserWithRoleResponse.from_domain(upr) for upr in user_project_roles],
                total=total,
                page=page,
                page_size=page_size,
                total_pages=(total + page_size - 1) // page_size
            )
        except ProjectError as e:
            raise HTTPException(status_code=404, detail=str(e)) from e
