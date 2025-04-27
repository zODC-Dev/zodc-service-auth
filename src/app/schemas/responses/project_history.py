from datetime import datetime
from typing import List, Optional

from src.app.schemas.responses.base import BaseResponse
from src.domain.entities.user_project_history import UserProjectHistory


class ProjectHistoryResponse(BaseResponse):
    id: int
    project_id: int
    project_name: str = ""
    project_key: str = ""
    position: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    description: Optional[str] = None
    technologies: List[str] = []

    @classmethod
    def from_domain(cls, history: UserProjectHistory) -> "ProjectHistoryResponse":
        # Handle potentially missing data
        if not history.data:
            history.data = {}

        # Extract data fields with safe defaults
        position = history.data.get("position")
        start_date = history.data.get("start_date")
        end_date = history.data.get("end_date")
        description = history.data.get("description")
        technologies = history.data.get("technologies", [])

        # Get project info safely
        project_name = ""
        project_key = ""
        if history.project:
            # Use getattr to safely get attributes that might not exist
            project_name = getattr(history.project, "name", "")
            project_key = getattr(history.project, "key", "")

        # Create response with safe defaults
        return cls(
            id=history.id,
            project_id=history.project_id,
            project_name=project_name,
            project_key=project_key,
            position=position,
            start_date=start_date,
            end_date=end_date,
            description=description,
            technologies=technologies or []
        )
