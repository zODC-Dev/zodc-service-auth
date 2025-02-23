from typing import List

from fastapi import HTTPException

from src.app.schemas.requests.project import LinkJiraProjectRequest, ProjectCreateRequest, ProjectUpdateRequest
from src.app.schemas.responses.project import ProjectResponse
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
    ) -> None:
        try:
            await self.project_service.link_jira_project(
                project_data=request,
                current_user_id=current_user_id
            )
        except (ProjectError, UnauthorizedError) as e:
            raise HTTPException(status_code=400, detail=str(e)) from e
