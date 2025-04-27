from fastapi import Depends

from src.app.controllers.internal_controller import InternalController
from src.app.dependencies.project import get_project_service
from src.app.dependencies.user import get_user_service


async def get_internal_controller(
    user_service=Depends(get_user_service),
    project_service=Depends(get_project_service)
):
    """Get dependencies for internal_controller"""
    return InternalController(user_service, project_service)
