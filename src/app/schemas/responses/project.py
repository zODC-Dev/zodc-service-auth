
from src.app.schemas.responses.base import BaseResponse
from src.domain.entities.project import Project


class ProjectResponse(BaseResponse):
    id: int
    name: str
    key: str
    description: str

    @classmethod
    def from_domain(cls, project: Project) -> 'ProjectResponse':
        return cls(
            id=project.id,
            name=project.name,
            key=project.key,
            description=project.description
        )
