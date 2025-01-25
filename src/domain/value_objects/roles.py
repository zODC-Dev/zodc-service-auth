from pydantic import BaseModel


class ProjectRole(BaseModel):
    project_name: str
    role_name: str


class SystemRole(BaseModel):
    role_name: str
