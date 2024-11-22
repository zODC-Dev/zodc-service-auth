# src/configs/redis_config.py
from redis.asyncio import Redis
from typing import Optional

from src.configs.settings import settings

_redis_client: Optional[Redis] = None

async def get_redis_client() -> Redis:
    global _redis_client
    if _redis_client:
        return _redis_client
    else:
        _redis_client = Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            # password=settings.REDIS_PASSWORD,
            # db=settings.REDIS_DB,
            decode_responses=True
        )
        return _redis_client
