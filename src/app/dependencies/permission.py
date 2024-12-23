from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from src.app.controllers.permission_controller import PermissionController
from src.app.services.permission_service import PermissionService
from src.configs.database import get_db
from src.infrastructure.repositories.sqlalchemy_permission_repository import SQLAlchemyPermissionRepository


async def get_permission_repository(db: AsyncSession = Depends(get_db)):
    """Get permission repository instance with database session."""
    return SQLAlchemyPermissionRepository(db)


async def get_permission_service(
    permission_repository=Depends(get_permission_repository)
):
    """Get permission service instance with repository dependency."""
    return PermissionService(permission_repository)


async def get_permission_controller(
    permission_service=Depends(get_permission_service)
):
    """Get permission controller instance with service dependency."""
    return PermissionController(permission_service)
