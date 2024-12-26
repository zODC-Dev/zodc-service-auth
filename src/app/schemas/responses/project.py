from pydantic import BaseModel

from src.domain.entities.project import Project


class ProjectResponse(BaseModel):
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
