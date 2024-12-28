from __future__ import annotations

from typing import Annotated, Any, Dict

from fastapi import Depends, HTTPException
import jwt
from sqlmodel.ext.asyncio.session import AsyncSession

from src.app.controllers.auth_controller import AuthController
from src.app.dependencies.user import get_user_repository
from src.app.services.auth_service import AuthService
from src.app.services.user_service import UserService
from src.configs.auth import JWT_SETTINGS, oauth2_scheme
from src.configs.database import get_db
from src.configs.logger import log
from src.domain.entities.user import User
from src.domain.exceptions.auth_exceptions import InvalidTokenError, TokenExpiredError
from src.infrastructure.repositories.sqlalchemy_auth_repository import SQLAlchemyAuthRepository
from src.infrastructure.repositories.sqlalchemy_user_repository import SQLAlchemyUserRepository
from src.infrastructure.services.jwt_token_service import JWTTokenService
from src.infrastructure.services.microsoft_sso_service import MicrosoftSSOService

from .common import get_redis_service, get_role_repository, get_token_service
from .user import get_user_service


async def get_auth_repository(db: AsyncSession = Depends(get_db), role_repository = Depends(get_role_repository)) -> SQLAlchemyAuthRepository:
    """Dependency for auth repository"""
    user_repository = SQLAlchemyUserRepository(db)
    return SQLAlchemyAuthRepository(session=db, user_repository=user_repository, role_repository=role_repository)

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

async def verify_token(
    token: Annotated[str, Depends(oauth2_scheme)],
    token_service: Annotated[JWTTokenService, Depends(get_token_service)]
) -> Dict[str, Any]:
    """Base token verification"""
    try:
        # Verify and decode token
        payload: Dict[str, Any] = jwt.decode(
            token,
            JWT_SETTINGS["SECRET_KEY"],
            algorithms=[JWT_SETTINGS["ALGORITHM"]]
        )
        return payload

    except jwt.ExpiredSignatureError as e:
        raise TokenExpiredError() from e
    except jwt.InvalidTokenError as e:
        raise InvalidTokenError() from e
    except Exception as e:
        log.error(f"Token verification error: {str(e)}")
        raise HTTPException(status_code=401, detail="Invalid token") from e

async def get_current_user_id(
    payload: Annotated[Dict[str, Any], Depends(verify_token)]
) -> int:
    """Extract user ID from verified token"""
    user_id = payload.get("sub")
    if not user_id:
        raise InvalidTokenError("Invalid token payload")
    return int(user_id)

async def get_current_user(
    user_id: Annotated[int, Depends(get_current_user_id)],
    user_service: Annotated[UserService, Depends(get_user_service)]
) -> User:
    """Get current user from database"""
    return await user_service.get_current_user(user_id)

# Reusable dependency types
TokenPayload = Annotated[Dict[str, Any], Depends(verify_token)]
CurrentUserId = Annotated[int, Depends(get_current_user_id)]
CurrentUser = Annotated[User, Depends(get_current_user)]
