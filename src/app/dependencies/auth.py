import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from redis.asyncio import Redis
from sqlmodel.ext.asyncio.session import AsyncSession

from src.app.controllers.auth_controller import AuthController
from src.app.dependencies.user import get_user_repository
from src.app.services.auth_service import AuthService
from src.configs.database import get_db
from src.configs.logger import logger
from src.configs.redis_config import get_redis_client
from src.domain.exceptions.auth_exceptions import InvalidTokenError, TokenExpiredError
from src.infrastructure.repositories.sqlalchemy_auth_repository import SQLAlchemyAuthRepository
from src.infrastructure.repositories.sqlalchemy_user_repository import SQLAlchemyUserRepository
from src.infrastructure.services.jwt_token_service import JWTTokenService
from src.infrastructure.services.microsoft_sso_service import MicrosoftSSOService
from src.infrastructure.services.redis_service import RedisService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

async def get_auth_repository(db: AsyncSession = Depends(get_db)) -> SQLAlchemyAuthRepository:
    """Dependency for auth repository"""
    user_repository = SQLAlchemyUserRepository(db)
    return SQLAlchemyAuthRepository(session=db, user_repository=user_repository)

async def get_redis_service(redis_client: Redis = Depends(get_redis_client)):
    """Dependency for redis repository"""
    return RedisService(redis_client=redis_client)

async def get_token_service(redis_client: RedisService = Depends(get_redis_service)):
    """Dependency for token service"""
    return JWTTokenService(redis_service=redis_client)

async def get_sso_service():
    """Dependency for SSO service"""
    return MicrosoftSSOService()

async def get_auth_service(
    auth_repository = Depends(get_auth_repository),
    token_service = Depends(get_token_service),
    sso_service = Depends(get_sso_service),
    user_repository = Depends(get_user_repository),
    redis_service = Depends(get_redis_service)
):
    """Dependency for auth service"""
    return AuthService(
        auth_repository=auth_repository,
        token_service=token_service,
        sso_service=sso_service,
        user_repository=user_repository,
        redis_service=redis_service
    )

async def get_auth_controller(
    auth_service = Depends(get_auth_service)
):
    """Dependency for auth controller"""
    return AuthController(auth_service)

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    token_service: JWTTokenService = Depends(get_token_service)
) -> int:
    """Get current user ID from JWT token

    Returns user_id instead of full user to avoid unnecessary DB queries
    """
    try:
        # Verify and decode token
        user_identity = await token_service.verify_token(token)
        if not user_identity:
            raise InvalidTokenError()

        logger.info(f"Authenticated user ID: {user_identity.id}")
        return user_identity.id

    except jwt.ExpiredSignatureError as e:
        raise TokenExpiredError() from e
    except jwt.InvalidTokenError as e:
        raise InvalidTokenError() from e
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials"
        ) from e
