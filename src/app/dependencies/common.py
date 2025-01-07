from fastapi import Depends
from redis.asyncio import Redis
from sqlmodel.ext.asyncio.session import AsyncSession

from src.configs.database import get_db
from src.configs.redis import get_redis_client
from src.infrastructure.repositories.sqlalchemy_refresh_token_repository import SQLAlchemyRefreshTokenRepository
from src.infrastructure.repositories.sqlalchemy_role_repository import SQLAlchemyRoleRepository
from src.infrastructure.repositories.sqlalchemy_user_repository import SQLAlchemyUserRepository
from src.infrastructure.services.jwt_token_service import JWTTokenService
from src.infrastructure.services.nats_service import NATSService
from src.infrastructure.services.redis_service import RedisService


async def get_refresh_token_repository(
    db: AsyncSession = Depends(get_db)
) -> SQLAlchemyRefreshTokenRepository:
    """Dependency for refresh token repository"""
    return SQLAlchemyRefreshTokenRepository(session=db)


async def get_user_repository(db: AsyncSession = Depends(get_db)) -> SQLAlchemyUserRepository:
    """Dependency for user repository"""
    return SQLAlchemyUserRepository(db)


async def get_redis_service(redis_client: Redis = Depends(get_redis_client)):
    """Dependency for redis repository"""
    return RedisService(redis_client=redis_client)


async def get_role_repository(db: AsyncSession = Depends(get_db)) -> SQLAlchemyRoleRepository:
    """Dependency for role repository"""
    return SQLAlchemyRoleRepository(db)


async def get_token_service(redis_service: RedisService = Depends(get_redis_service), role_repository: SQLAlchemyRoleRepository = Depends(get_role_repository), user_repository: SQLAlchemyUserRepository = Depends(get_user_repository), refresh_token_repository: SQLAlchemyRefreshTokenRepository = Depends(get_refresh_token_repository)):
    """Dependency for token service"""
    return JWTTokenService(redis_service=redis_service, role_repository=role_repository, user_repository=user_repository, refresh_token_repository=refresh_token_repository)


async def get_nats_service():
    """Dependency for NATS service"""
    nats_service = NATSService()
    await nats_service.connect()
    return nats_service
