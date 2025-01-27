from typing import List

from pydantic import BaseModel

from src.domain.entities.permission import Permission


class ProjectPermission(BaseModel):
    project_id: int
    project_name: str
    permissions: List[Permission]


class SystemPermission(BaseModel):
    permissions: List[Permission]
