from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from src.app.controllers.project_controller import ProjectController
from src.app.dependencies.common import get_nats_service, get_redis_service, get_role_repository, get_user_repository
from src.app.services.project_service import ProjectService
from src.configs.database import get_db
from src.infrastructure.repositories.sqlalchemy_project_repository import SQLAlchemyProjectRepository


async def get_project_repository(db: AsyncSession = Depends(get_db)):
    """Get the project repository."""
    return SQLAlchemyProjectRepository(db)


async def get_project_service(
    project_repository=Depends(get_project_repository),
    role_repository=Depends(get_role_repository),
    user_repository=Depends(get_user_repository),
    nats_service=Depends(get_nats_service),
    redis_service=Depends(get_redis_service)
):
    """Get the project service."""
    return ProjectService(project_repository, role_repository, user_repository, nats_service, redis_service)


async def get_project_controller(
    project_service=Depends(get_project_service)
):
    """Get the project controller."""
    return ProjectController(project_service)
