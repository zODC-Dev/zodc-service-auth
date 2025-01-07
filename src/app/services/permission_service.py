from typing import List, Optional

from src.configs.logger import log
from src.domain.entities.permission import Permission, PermissionVerificationPayload, PermissionVerificationResult
from src.domain.exceptions.auth_exceptions import TokenExpiredError
from src.domain.repositories.permission_repository import IPermissionRepository
from src.domain.repositories.user_repository import IUserRepository
from src.domain.services.permission_service import IPermissionService
from src.domain.services.redis_service import IRedisService
from src.domain.services.token_service import ITokenService


class PermissionService(IPermissionService):
    def __init__(
        self,
        token_service: ITokenService,
        redis_service: IRedisService,
        permission_repository: IPermissionRepository,
        user_repository: IUserRepository
    ):
        self.token_service = token_service
        self.redis_service = redis_service
        self.permission_repository = permission_repository
        self.user_repository = user_repository

    async def get_all_permissions(self) -> List[Permission]:
        return await self.permission_repository.get_all_permissions()

    async def verify_permission(
        self,
        payload: PermissionVerificationPayload
    ) -> PermissionVerificationResult:
        try:
            # Check cache first
            cache_key = f"perm:{payload.user_id}:{payload.scope}"
            if payload.project_id:
                cache_key += f":{payload.project_id}"
            cache_key += f":{','.join(sorted(payload.permissions))}"

            cached_result: Optional[str] = await self.redis_service.get(cache_key)
            if cached_result is not None:
                return PermissionVerificationResult(
                    allowed=cached_result == "1",
                    user_id=payload.user_id,
                    permissions=payload.permissions,
                    scope=payload.scope,
                    project_id=payload.project_id
                )

            # Verify token contains correct user info
            db_user = await self.token_service.verify_token(payload.token)
            if not db_user or str(payload.user_id) != str(db_user.id):
                return PermissionVerificationResult(
                    allowed=False,
                    user_id=payload.user_id,
                    permissions=payload.permissions,
                    scope=payload.scope,
                    project_id=payload.project_id,
                    error="Invalid token"
                )

            # Get user's permissions from database
            allowed = False
            if payload.scope == "system":
                user_permissions = await self.permission_repository.get_user_system_permissions(
                    payload.user_id
                )
                user_permission_names = [p.name for p in user_permissions]
                # Check if user has ALL required permissions
                allowed = all(
                    perm in user_permission_names for perm in payload.permissions)

            elif payload.scope == "project" and payload.project_id:
                user_permissions = await self.permission_repository.get_user_project_permissions(
                    payload.user_id,
                    payload.project_id
                )
                user_permission_names = [p.name for p in user_permissions]
                # Check if user has ALL required permissions
                allowed = all(
                    perm in user_permission_names for perm in payload.permissions)

            # Cache the result
            await self.redis_service.set(
                cache_key,
                {"allowed": allowed},
                expiry=300  # 5 minutes cache
            )

            return PermissionVerificationResult(
                allowed=allowed,
                user_id=payload.user_id,
                permissions=payload.permissions,
                scope=payload.scope,
                project_id=payload.project_id
            )

        except TokenExpiredError:
            return PermissionVerificationResult(
                allowed=False,
                user_id=payload.user_id,
                permissions=payload.permissions,
                scope=payload.scope,
                project_id=payload.project_id,
                error="Token expired"
            )
        except Exception as e:
            log.error(f"Error verifying permission: {str(e)}")
            return PermissionVerificationResult(
                allowed=False,
                user_id=payload.user_id,
                permissions=payload.permissions,
                scope=payload.scope,
                project_id=payload.project_id,
                error=str(e)
            )
