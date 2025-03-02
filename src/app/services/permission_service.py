from typing import List

from src.domain.entities.permission import Permission
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
