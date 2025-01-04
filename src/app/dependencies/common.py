from fastapi import Depends
from redis.asyncio import Redis
from sqlmodel.ext.asyncio.session import AsyncSession

from src.configs.database import get_db
from src.configs.redis_config import get_redis_client
from src.infrastructure.repositories.sqlalchemy_role_repository import SQLAlchemyRoleRepository
from src.infrastructure.services.jwt_token_service import JWTTokenService
from src.infrastructure.services.nats_service import NATSService
from src.infrastructure.services.redis_service import RedisService


async def get_redis_service(redis_client: Redis = Depends(get_redis_client)):
    """Dependency for redis repository"""
    return RedisService(redis_client=redis_client)


async def get_role_repository(db: AsyncSession = Depends(get_db)) -> SQLAlchemyRoleRepository:
    """Dependency for role repository"""
    return SQLAlchemyRoleRepository(db)


async def get_token_service(redis_client: RedisService = Depends(get_redis_service), role_repository=Depends(get_role_repository)):
    """Dependency for token service"""
    return JWTTokenService(redis_service=redis_client, role_repository=role_repository)


async def get_nats_service():
    """Dependency for NATS service"""
    nats_service = NATSService()
    await nats_service.connect()
    return nats_service
