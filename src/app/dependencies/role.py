from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from src.app.controllers.role_controller import RoleController
from src.app.services.role_service import RoleService
from src.configs.database import get_db
from src.infrastructure.repositories.sqlalchemy_project_repository import SQLAlchemyProjectRepository

from .common import get_permission_repository, get_role_repository, get_user_repository


async def get_project_repository(db: AsyncSession = Depends(get_db)):
    """Get dependencies for project_repository"""
    return SQLAlchemyProjectRepository(db)


async def get_role_service(
    role_repository=Depends(get_role_repository),
    permission_repository=Depends(get_permission_repository),
    project_repository=Depends(get_project_repository),
    user_repository=Depends(get_user_repository)
):
    """Get dependencies for role_service"""
    return RoleService(role_repository, permission_repository, project_repository, user_repository)


async def get_role_controller(
    role_service=Depends(get_role_service)
):
    """Get dependencies for role_controller"""
    return RoleController(role_service)
