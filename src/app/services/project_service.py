from typing import List

from src.domain.entities.project import Project, ProjectCreate, ProjectUpdate
from src.domain.exceptions.project_exceptions import ProjectKeyAlreadyExistsError, ProjectNotFoundError
from src.domain.repositories.project_repository import IProjectRepository


class ProjectService:
    def __init__(self, project_repository: IProjectRepository):
        self.project_repository = project_repository

    async def create_project(self, project_data: ProjectCreate) -> Project:
        existing_project = await self.project_repository.get_project_by_key(project_data.key)
        if existing_project:
            raise ProjectKeyAlreadyExistsError(
                f"Project with key '{project_data.key}' already exists")
        return await self.project_repository.create_project(project_data)

    async def get_project(self, project_id: int) -> Project:
        project = await self.project_repository.get_project_by_id(project_id)
        if not project:
            raise ProjectNotFoundError(
                f"Project with id {project_id} not found")
        return project

    async def get_all_projects(self) -> List[Project]:
        return await self.project_repository.get_all_projects()

    async def update_project(self, project_id: int, project_data: ProjectUpdate) -> Project:
        project = await self.project_repository.get_project_by_id(project_id)
        if not project:
            raise ProjectNotFoundError(
                f"Project with id {project_id} not found")
        return await self.project_repository.update_project(project_id, project_data)

    async def delete_project(self, project_id: int) -> None:
        project = await self.project_repository.get_project_by_id(project_id)
        if not project:
            raise ProjectNotFoundError(
                f"Project with id {project_id} not found")
        await self.project_repository.delete_project(project_id)

    async def get_user_projects(self, user_id: int) -> List[Project]:
        return await self.project_repository.get_user_projects(user_id)
