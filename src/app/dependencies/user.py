from fastapi import Depends

from src.app.controllers.user_controller import UserController
from src.app.services.user_service import UserService

from .common import get_redis_service, get_user_repository


async def get_user_service(
    user_repository=Depends(get_user_repository),
    redis_service=Depends(get_redis_service)
):
    """Get dependencies for user_service"""
    return UserService(user_repository=user_repository, redis_service=redis_service)


async def get_user_controller(
    user_service=Depends(get_user_service)
):
    """Get dependencies for user_controller"""
    return UserController(user_service)
