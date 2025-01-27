from pydantic import BaseModel


class ProjectRole(BaseModel):
    project_id: int
    role_name: str


class SystemRole(BaseModel):
    role_name: str
