from functools import wraps
from typing import Any, Dict, List, Optional, cast

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
    """Permission checking decorator"""
    def decorator(func):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            try:
                # Get token from Authorization header
                auth_header = request.headers.get('Authorization')
                if not auth_header or not auth_header.startswith('Bearer '):
                    raise HTTPException(status_code=401, detail="Missing or invalid token")

                # Verify JWT token
                access_token = auth_header.split(' ')[1]
                token_payload = jwt.decode(
                    access_token,
                    settings.JWT_SECRET,
                    algorithms=[settings.JWT_ALGORITHM]
                )

                # Add user info to request state
                request.state.user = token_payload

                # Check permissions
                if not _check_permissions(
                    token_payload,
                    request,
                    system_roles,
                    project_roles,
                    permissions,
                    require_all
                ):
                    raise HTTPException(
                        status_code=403,
                        detail="Insufficient permissions"
                    )
                return await func(request, *args, **kwargs)
            except jwt.ExpiredSignatureError as e:
                raise HTTPException(status_code=401, detail="Token has expired") from e
            except jwt.InvalidTokenError as e:
                raise HTTPException(status_code=401, detail="Invalid token") from e
            except Exception as e:
                log.error(f"Permission check error: {str(e)}")
                raise HTTPException(status_code=403, detail="Permission check failed") from e
        return wrapper
    return decorator

def _check_permissions(
    payload: Dict[str, Any],
    request: Request,
    system_roles: Optional[List[str]],
    project_roles: Optional[List[str]],
    permissions: Optional[List[str]],
    require_all: bool
) -> bool:
    """Centralized permission checking logic"""
    # Check system roles
    if system_roles and not _check_system_roles(payload, system_roles):
        return False

    # Check project roles
    if project_roles and not _check_project_roles(
        payload, request, project_roles, require_all
    ):
        return False

    # Check permissions
    if permissions and not _check_user_permissions(payload, permissions, require_all):
        return False

    return True

def _check_system_roles(payload: Dict[str, Any], required_roles: List[str]) -> bool:
    user_role = payload.get("system_role")
    log.info(f"User role: {user_role}")
    return (user_role is not None) and (user_role in required_roles)


def _check_project_roles(
    payload: Dict[str, Any],
    request: Request,
    required_roles: List[str],
    require_all: bool
) -> bool:
    project_id = _get_project_id(request)
    if not project_id:
        return False

    user_project_roles = payload.get("project_roles", {})
    user_roles = user_project_roles.get(str(project_id), [])

    if require_all:
        return all(role in user_roles for role in required_roles)
    return any(role in user_roles for role in required_roles)

def _check_user_permissions(
    payload: Dict[str, Any],
    required_permissions: List[str],
    require_all: bool
) -> bool:
    user_permissions = payload.get("permissions", [])
    if require_all:
        return all(perm in user_permissions for perm in required_permissions)
    return any(perm in user_permissions for perm in required_permissions)

def _get_project_id(request: Request) -> Optional[str]:
    """Extract project_id from request"""
    return (
        cast(str, request.path_params.get("project_id")) or
        request.query_params.get("project_id")
    )
