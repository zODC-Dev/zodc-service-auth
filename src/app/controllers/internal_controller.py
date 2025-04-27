from typing import Any, Dict, List

from fastapi import HTTPException

from src.app.schemas.responses.base import StandardResponse
from src.app.schemas.responses.user import UserWithProfileResponse
from src.app.services.project_service import ProjectService
from src.app.services.user_service import UserService
from src.domain.entities.user import User
from src.domain.exceptions.project_exceptions import ProjectNotFoundError
from src.domain.exceptions.user_exceptions import UserNotFoundError


class InternalController:
    def __init__(self, user_service: UserService, project_service: ProjectService):
        self.user_service = user_service
        self.project_service = project_service

    async def get_users_by_ids(self, user_ids: List[int]) -> StandardResponse[List[UserWithProfileResponse]]:
        """Get users by list of IDs. This is an internal API for microservice."""
        users: List[UserWithProfileResponse] = []
        errors: List[Dict[str, Any]] = []

        for user_id in user_ids:
            try:
                user = await self.user_service.get_current_user(user_id)
                users.append(UserWithProfileResponse.from_domain(user))
            except UserNotFoundError as e:
                errors.append({"user_id": user_id, "error": str(e)})
            except Exception as e:
                errors.append({"user_id": user_id, "error": f"Unexpected error: {str(e)}"})

        return StandardResponse(
            message="Users retrieved successfully",
            data=users,
        )

    async def get_users_by_project_key(self, project_key: str) -> StandardResponse[List[User]]:
        """Get users by project key. This is an internal API for microservice."""
        try:
            project = await self.project_service.get_project(project_key=project_key)
            if not project:
                raise ProjectNotFoundError(f"Project with key {project_key} not found")
            assert project.id is not None, "Project ID is required"

            users = await self.user_service.get_users_by_project_id(project_id=project.id)
            return StandardResponse(
                message="Users retrieved successfully",
                data=users,
            )
        except ProjectNotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e)) from e
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e)) from e
