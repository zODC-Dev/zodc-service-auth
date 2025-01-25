from typing import Any, Dict, List, Optional

from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import jwt

from src.configs.settings import settings

security = HTTPBearer()


class JWTAuth:
    def __init__(
        self,
        required_system_roles: Optional[List[str]] = None,
        required_project_roles: Optional[List[str]] = None,
        required_permissions: Optional[List[str]] = None,
        require_all_roles: bool = False
    ):
        self.required_system_roles = required_system_roles or []
        self.required_project_roles = required_project_roles or []
        self.required_permissions = required_permissions or []
        self.require_all_roles = require_all_roles
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
                settings.JWT_PRIVATE_KEY_PATH,
                algorithms=[settings.JWT_ALGORITHM]
            )

            # Add user info to request state
            request.state.user = payload

            if not self._validate_access(payload, request):
                raise HTTPException(
                    status_code=403,
                    detail="Insufficient permissions"
                )

            return payload

        except jwt.ExpiredSignatureError as e:
            raise HTTPException(
                status_code=401,
                detail="Token has expired"
            ) from e
        except jwt.InvalidTokenError as e:
            raise HTTPException(
                status_code=401,
                detail="Invalid token"
            ) from e
        except Exception as e:
            raise HTTPException(
                status_code=401,
                detail=str(e)
            ) from e

    def _validate_access(self, payload: Dict[str, Any], request: Request) -> bool:
        """Validate system roles, project roles and permissions"""
        # Check system roles if required
        if self.required_system_roles and not self._check_system_roles(payload):
            return False

        # Check project roles if required
        if self.required_project_roles and not self._check_project_roles(payload, request):
            return False

        # Check permissions if required
        if self.required_permissions and not self._check_permissions(payload):
            return False

        return True

    def _check_system_roles(self, payload: Dict[str, Any]) -> bool:
        """Check if user has required system roles"""
        user_system_role = payload.get("system_role")
        if not user_system_role:
            return False

        if self.require_all_roles:
            return all(role == user_system_role for role in self.required_system_roles)
        return user_system_role in self.required_system_roles

    def _check_project_roles(self, payload: Dict[str, Any], request: Request) -> bool:
        """Check if user has required project roles"""
        # Get project_id from request path or query parameters
        project_id = self._get_project_id(request)
        if not project_id:
            return False

        user_project_roles = payload.get("project_roles", {})
        project_roles = user_project_roles.get(str(project_id), [])

        if self.require_all_roles:
            return all(role in project_roles for role in self.required_project_roles)
        return any(role in project_roles for role in self.required_project_roles)

    def _check_permissions(self, payload: Dict[str, Any]) -> bool:
        """Check if user has required permissions"""
        user_permissions = payload.get("permissions", [])
        return any(perm in user_permissions for perm in self.required_permissions)

    def _get_project_id(self, request: Request) -> Optional[int]:
        """Extract project_id from request path parameters or query parameters"""
        # Try to get from path parameters first
        project_id = request.path_params.get("project_id")
        if not project_id:
            # Try to get from query parameters
            project_id = request.query_params.get("project_id")

        return int(project_id) if project_id else None
