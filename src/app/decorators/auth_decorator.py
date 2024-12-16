from functools import wraps
from typing import List, Optional

from fastapi import HTTPException, Request
import jwt

from src.configs.logger import log
from src.configs.settings import settings


def require_permissions(
    system_roles: Optional[List[str]] = None,
    project_roles: Optional[List[str]] = None,
    permissions: Optional[List[str]] = None,
    require_all: bool = False
):
    """Decorator for checking user permission"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request: Request = kwargs.get('request')
            if not request:
                raise HTTPException(status_code=401, detail="Unauthorized")

            # Get token from Authorization header
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                raise HTTPException(status_code=401, detail="Missing or invalid token")

            try:
                # Verify JWT token
                token = auth_header.split(' ')[1]
                payload = jwt.decode(
                    token,
                    settings.JWT_SECRET,
                    algorithms=[settings.JWT_ALGORITHM]
                )

                # Add user info to request state
                request.state.user = payload
                user = payload

                log.info(f"User: {user}")

                # Check system roles if required
                if system_roles:
                    user_system_role = user.get('system_role')
                    if not user_system_role or user_system_role not in system_roles:
                        raise HTTPException(status_code=403, detail="Insufficient system role")

                # Check project roles if required
                if project_roles:
                    project_id = str(_get_project_id(request))
                    if not project_id:
                        raise HTTPException(status_code=400, detail="Project ID is required")

                    user_project_roles = user.get('project_roles', {})
                    user_roles = user_project_roles.get(project_id, [])

                    if require_all and not all(role in user_roles for role in project_roles):
                        raise HTTPException(status_code=403, detail="Insufficient project roles")
                    elif not require_all and not any(role in user_roles for role in project_roles):
                        raise HTTPException(status_code=403, detail="Insufficient project roles")

                # Check permissions if required
                if permissions:
                    user_permissions = user.get('permissions', [])
                    if not any(perm in user_permissions for perm in permissions):
                        raise HTTPException(status_code=403, detail="Insufficient permissions")

                return await func(*args, **kwargs)

            except jwt.ExpiredSignatureError as e:
                raise HTTPException(status_code=401, detail="Token has expired") from e
            except jwt.InvalidTokenError as e:
                raise HTTPException(status_code=401, detail="Invalid token") from e
            except Exception as e:
                log.error(f"Auth error: {str(e)}")
                raise HTTPException(status_code=401, detail="Authentication failed") from e

        return wrapper
    return decorator


def _get_project_id(request: Request) -> Optional[str]:
    """Extract project_id from request path parameters or query parameters"""
    # Try to get from path parameters first
    project_id: str | None = request.path_params.get("project_id")
    if not project_id:
        # Try to get from query parameters
        project_id = request.query_params.get("project_id")

    return project_id
