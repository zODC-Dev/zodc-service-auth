from typing import Optional

from sqlalchemy.orm import selectinload
from sqlmodel import col, select, update
from sqlmodel.ext.asyncio.session import AsyncSession

from src.configs.logger import log
from src.domain.constants.nats_events import NATSPublishTopic
from src.domain.entities.user import User as UserEntity, UserCreate, UserUpdate, UserWithPassword
from src.domain.repositories.user_repository import IUserRepository
from src.domain.services.redis_service import IRedisService
from src.domain.services.user_event_service import IUserEventService
from src.infrastructure.models.permission import Permission as PermissionModel
from src.infrastructure.models.role import Role as RoleModel
from src.infrastructure.models.role_permission import RolePermission as RolePermissionModel
from src.infrastructure.models.user import User as UserModel
from src.infrastructure.models.user_project_role import UserProjectRole as UserProjectRoleModel


class SQLAlchemyUserRepository(IUserRepository):
    def __init__(
        self,
        session: AsyncSession,
        user_event_service: IUserEventService,
        redis_service: IRedisService
    ):
        self.session = session
        self.user_event_service = user_event_service
        self.redis_service = redis_service

    async def get_user_by_id(self, user_id: int) -> Optional[UserEntity]:
        # Load user with system role and permissions
        stmt = (
            select(UserModel)
            .options(
                selectinload(UserModel.system_role).selectinload(  # type: ignore
                    RoleModel.permissions),  # type: ignore
                selectinload(UserModel.user_project_roles).selectinload(UserProjectRoleModel.role).selectinload(  # type: ignore
                    RoleModel.permissions),  # type: ignore
                selectinload(UserModel.user_project_roles).selectinload(UserProjectRoleModel.project)  # type: ignore
            )
            .where(UserModel.id == int(user_id))
        )
        result = await self.session.exec(stmt)
        user = result.first()

        if not user:
            return None

        # Create a simplified system_role without nested relationships
        system_role = None
        if user.system_role:
            system_role = {
                "id": user.system_role.id,
                "name": user.system_role.name,
                "description": user.system_role.description,
                "is_system_role": user.system_role.is_system_role,
                "is_active": user.system_role.is_active,
                "created_at": user.system_role.created_at,
                "updated_at": user.system_role.updated_at,
                "permissions": [
                    {"id": p.id, "name": p.name, "description": p.description}
                    for p in user.system_role.permissions
                ] if user.system_role.permissions else []
            }

        # Create simplified user_project_roles with project and role information
        user_project_roles = []
        if user.user_project_roles:
            for upr in user.user_project_roles:
                project = None
                if upr.project:
                    project = {
                        "id": upr.project.id,
                        "name": upr.project.name,
                        "key": upr.project.key,
                        "description": upr.project.description,
                        "avatar_url": upr.project.avatar_url
                    }

                role = None
                if upr.role:
                    role = {
                        "id": upr.role.id,
                        "name": upr.role.name,
                        "description": upr.role.description,
                        "is_system_role": upr.role.is_system_role,
                        "is_active": upr.role.is_active,
                        "permissions": [
                            {"id": p.id, "name": p.name, "description": p.description}
                            for p in upr.role.permissions
                        ] if upr.role.permissions else []
                    }

                user_project_roles.append({
                    "user_id": upr.user_id,
                    "project_id": upr.project_id,
                    "role_id": upr.role_id,
                    "created_at": upr.created_at,
                    "updated_at": upr.updated_at,
                    "project": project,
                    "role": role
                })

        return UserEntity(
            id=user.id,
            email=user.email,
            name=user.name,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at,
            system_role=system_role,
            user_project_roles=user_project_roles,
            is_jira_linked=user.is_jira_linked,
            jira_account_id=user.jira_account_id,
            avatar_url=user.avatar_url
        )

    async def get_user_by_id_with_role_permissions(self, user_id: int) -> Optional[UserEntity]:
        stmt = (
            select(UserModel)
            .options(selectinload(UserModel.system_role))  # type: ignore
            .where(UserModel.id == int(user_id))
        )
        result = await self.session.exec(stmt)
        user = result.first()

        if not user:
            return None

        # Create a simplified system_role without nested relationships
        system_role = None
        if user.system_role:
            # Get permissions for this role
            permissions_stmt = (
                select(PermissionModel)
                .join(RolePermissionModel, col(PermissionModel.id) == col(RolePermissionModel.permission_id))
                .where(col(RolePermissionModel.role_id) == col(user.system_role.id))
            )
            permissions_result = await self.session.exec(permissions_stmt)
            permissions = [{"id": p.id, "name": p.name, "description": p.description}
                           for p in permissions_result.all()]

            system_role = {
                "id": user.system_role.id,
                "name": user.system_role.name,
                "description": user.system_role.description,
                "is_system_role": user.system_role.is_system_role,
                "is_active": user.system_role.is_active,
                "created_at": user.system_role.created_at,
                "updated_at": user.system_role.updated_at,
                "permissions": permissions
            }

        # Create simplified user_project_roles without nested relationships
        user_project_roles = []
        if user.user_project_roles:
            for upr in user.user_project_roles:
                user_project_roles.append({
                    "user_id": upr.user_id,
                    "project_id": upr.project_id,
                    "role_id": upr.role_id,
                    "created_at": upr.created_at,
                    "updated_at": upr.updated_at
                })

        return UserEntity(
            id=user.id,
            email=user.email,
            name=user.name,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at,
            system_role=system_role,
            user_project_roles=user_project_roles,
            is_jira_linked=user.is_jira_linked,
            jira_account_id=user.jira_account_id,
            is_system_user=user.is_system_user,
            avatar_url=user.avatar_url,
        )

    async def get_user_by_email(self, email: str) -> Optional[UserEntity]:
        try:
            result = await self.session.exec(
                select(UserModel).where(UserModel.email == email)
            )
            user = result.first()
            return self._to_domain(user) if user else None
        except Exception as e:
            log.error(f"{str(e)}")
            return None

    async def get_user_with_password_by_email(self, email: str) -> Optional[UserWithPassword]:
        try:
            result = await self.session.exec(
                select(UserModel).where(UserModel.email == email)
            )
            user = result.first()
            return self._to_domain_with_password(user) if user else None
        except Exception as e:
            log.error(f"{str(e)}")
            return None

    async def create_user(self, user: UserCreate) -> UserEntity:
        """Create new user"""
        try:
            # Convert domain entity to DB model
            db_user = UserModel(
                email=user.email,
                name=user.name,
                is_active=user.is_active,
                jira_account_id=user.jira_account_id,
                is_jira_linked=user.is_jira_linked
            )

            self.session.add(db_user)
            await self.session.commit()
            await self.session.refresh(db_user)

            # Publish user created event
            if db_user and db_user.id is not None:
                await self.user_event_service.publish_user_event(
                    user_id=db_user.id,
                    event_type=NATSPublishTopic.USER_CREATED,
                    data=user.model_dump(exclude_none=True)
                )

            return self._to_domain(db_user)

        except Exception as e:
            log.error(f"Error creating user: {str(e)}")
            await self.session.rollback()
            raise

    async def update_user_by_id(self, user_id: int, user: UserUpdate) -> None:
        stmt = (
            update(UserModel).where(UserModel.id == user_id).values(  # type: ignore
                **user.model_dump(exclude={"id"}, exclude_none=True))
        )
        await self.session.exec(stmt)  # type: ignore
        await self.session.commit()

        # Publish user update event
        await self.user_event_service.publish_user_event(
            user_id=user_id,
            event_type=NATSPublishTopic.USER_UPDATED,
            data=user.model_dump(exclude_none=True)
        )

        # If user is being activated/deactivated, publish specific event
        if user.is_active is not None:
            event_type = NATSPublishTopic.USER_ACTIVATED if user.is_active else NATSPublishTopic.USER_DEACTIVATED
            await self.user_event_service.publish_user_event(
                user_id=user_id,
                event_type=event_type
            )

        # clear cache in redis with key user:{user_id}
        await self.redis_service.delete(f"user:{user_id}")

    async def get_user_by_jira_account_id(self, jira_account_id: str) -> Optional[UserEntity]:
        result = await self.session.exec(
            select(UserModel).where(UserModel.jira_account_id == jira_account_id)
        )
        user = result.first()
        return self._to_domain(user) if user else None

    def _to_domain(self, db_user: UserModel) -> UserEntity:
        """Convert DB model to domain entity"""
        # Create a simplified system_role without nested relationships
        system_role = None
        if db_user.system_role:
            system_role = {
                "id": db_user.system_role.id,
                "name": db_user.system_role.name,
                "description": db_user.system_role.description,
                "is_system_role": db_user.system_role.is_system_role,
                "is_active": db_user.system_role.is_active,
                "created_at": db_user.system_role.created_at,
                "updated_at": db_user.system_role.updated_at
            }

        # Create simplified user_project_roles without nested relationships
        user_project_roles = []
        if db_user.user_project_roles:
            for upr in db_user.user_project_roles:
                user_project_roles.append({
                    "user_id": upr.user_id,
                    "project_id": upr.project_id,
                    "role_id": upr.role_id,
                    "created_at": upr.created_at,
                    "updated_at": upr.updated_at
                })

        return UserEntity(
            id=db_user.id,
            email=db_user.email,
            name=db_user.name,
            is_active=db_user.is_active,
            created_at=db_user.created_at,
            updated_at=db_user.updated_at,
            system_role=system_role,
            user_project_roles=user_project_roles,
            is_jira_linked=db_user.is_jira_linked,
            jira_account_id=db_user.jira_account_id,
            is_system_user=db_user.is_system_user,
            avatar_url=db_user.avatar_url,
        )

    def _to_domain_with_password(self, db_user: UserModel) -> UserWithPassword:
        # Create a simplified system_role without nested relationships
        system_role = None
        if db_user.system_role:
            system_role = {
                "id": db_user.system_role.id,
                "name": db_user.system_role.name,
                "description": db_user.system_role.description,
                "is_system_role": db_user.system_role.is_system_role,
                "is_active": db_user.system_role.is_active,
                "created_at": db_user.system_role.created_at,
                "updated_at": db_user.system_role.updated_at
            }

        # Create simplified user_project_roles without nested relationships
        user_project_roles = []
        if db_user.user_project_roles:
            for upr in db_user.user_project_roles:
                user_project_roles.append({
                    "user_id": upr.user_id,
                    "project_id": upr.project_id,
                    "role_id": upr.role_id,
                    "created_at": upr.created_at,
                    "updated_at": upr.updated_at
                })

        return UserWithPassword(
            id=db_user.id,
            email=db_user.email,
            name=db_user.name,
            is_active=db_user.is_active,
            password=db_user.password,
            created_at=db_user.created_at,
            updated_at=db_user.updated_at,
            system_role=system_role,
            user_project_roles=user_project_roles,
            is_jira_linked=db_user.is_jira_linked,
            jira_account_id=db_user.jira_account_id,
        )
