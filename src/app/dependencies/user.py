from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from src.app.controllers.user_controller import UserController
from src.app.dependencies.common import get_redis_service, get_user_repository
from src.app.services.user_service import UserService
from src.configs.database import get_db
from src.domain.repositories.user_performance_repository import IUserPerformanceRepository
from src.domain.repositories.user_repository import IUserRepository
from src.domain.services.redis_service import IRedisService
from src.infrastructure.repositories.sqlalchemy_user_performance_repository import SQLAlchemyUserPerformanceRepository


async def get_user_performance_repository(db: AsyncSession = Depends(get_db)) -> IUserPerformanceRepository:
    """Get the user performance repository"""
    return SQLAlchemyUserPerformanceRepository(db)


async def get_user_service(
    user_repository: IUserRepository = Depends(get_user_repository),
    user_performance_repository: IUserPerformanceRepository = Depends(get_user_performance_repository),
    redis_service: IRedisService = Depends(get_redis_service)
) -> UserService:
    """Get the user service"""
    return UserService(
        user_repository,
        user_performance_repository,
        redis_service
    )


async def get_user_controller(
    user_service: UserService = Depends(get_user_service)
) -> UserController:
    """Get the user controller"""
    return UserController(user_service)
