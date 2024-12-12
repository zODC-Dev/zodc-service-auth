from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from src.app.controllers.user_controller import UserController
from src.app.services.user_service import UserService
from src.configs.database import get_db
from src.infrastructure.repositories.sqlalchemy_user_repository import SQLAlchemyUserRepository


async def get_user_repository(db: AsyncSession = Depends(get_db)):
    """Get dependencies for user_repository"""
    return SQLAlchemyUserRepository(db)

async def get_user_service(
    user_repository = Depends(get_user_repository)
):
    """Get dependencies for user_service"""
    return UserService(user_repository)

async def get_user_controller(
    user_service = Depends(get_user_service)
):
    """Get dependencies for user_controller"""
    return UserController(user_service)
