from typing import Any, List, Optional

import jwt
from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.configs.settings import settings
from src.domain.exceptions.auth_exceptions import AuthException

security = HTTPBearer()

class JWTAuth:
    def __init__(
        self,
        required_roles: Optional[List[str]] = None,
        required_permissions: Optional[List[str]] = None
    ):
        self.required_roles = required_roles or []
        self.required_permissions = required_permissions or []
        self.security = HTTPBearer()

    async def __call__(
        self,
        request: Request,
        credentials: HTTPAuthorizationCredentials = Depends(security)
    ):
        try:
            token = credentials.credentials
            payload = jwt.decode(
                token,
                settings.JWT_SECRET,
                algorithms=[settings.JWT_ALGORITHM]
            )

            # Add user info to request state
            request.state.user = payload

            # Check roles if required
            if self.required_roles and not self._check_roles(payload):
                raise AuthException.INSUFFICIENT_PERMISSIONS

            # Check permissions if required
            if self.required_permissions and not self._check_permissions(payload):
                raise AuthException.INSUFFICIENT_PERMISSIONS

            return payload

        except jwt.ExpiredSignatureError as e:
            raise AuthException.TOKEN_EXPIRED from e
        except jwt.InvalidTokenError as e:
            raise AuthException.INVALID_TOKEN from e
        except Exception as e:
            raise HTTPException(status_code=401, detail=str(e)) from e

    def _check_roles(self, payload: dict[str, Any]) -> bool:
        user_roles = payload.get("roles", [])
        return any(role in user_roles for role in self.required_roles)

    def _check_permissions(self, payload: dict[str, Any]) -> bool:
        user_permissions = payload.get("permissions", [])
        return any(perm in user_permissions for perm in self.required_permissions)
