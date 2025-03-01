from typing import List, Optional, Tuple

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import selectinload
from sqlmodel import and_, asc, col, delete, desc, func, or_, select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.domain.entities.permission import Permission as PermissionEntity
from src.domain.entities.project import Project as ProjectEntity
from src.domain.entities.role import Role as RoleEntity, RoleCreate, RoleUpdate
from src.domain.entities.user import User as UserEntity
from src.domain.entities.user_project_role import UserProjectRole as UserProjectRoleEntity
from src.domain.exceptions.role_exceptions import (
    InvalidPermissionIdsError,
    RoleAlreadyExistsError,
    RoleCreateError,
    RoleError,
    RoleIsSystemRoleError,
    RoleNotFoundError,
    RoleUpdateError,
)
from src.domain.exceptions.user_exceptions import UserNotFoundError
from src.domain.repositories.role_repository import IRoleRepository
from src.domain.value_objects.roles import ProjectRole, SystemRole
from src.infrastructure.models.permission import Permission
from src.infrastructure.models.project import Project
from src.infrastructure.models.role import Role
from src.infrastructure.models.role_permission import RolePermission
from src.infrastructure.models.user import User
from src.infrastructure.models.user_project_role import UserProjectRole


class SQLAlchemyRoleRepository(IRoleRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    def _permission_to_domain(self, permission: Permission) -> PermissionEntity:
        return PermissionEntity(
            id=permission.id,
            name=permission.name,
            description=permission.description
        )

    def _to_domain(self, role: Role) -> RoleEntity:
        return RoleEntity(
            id=role.id,
            name=role.name,
            description=role.description,
            is_system_role=role.is_system_role,
            is_active=role.is_active,
            permissions=[self._permission_to_domain(
                p) for p in role.permissions]
        )

    def _to_domain_user_project_role(self, upr: UserProjectRole) -> UserProjectRoleEntity:
        return UserProjectRoleEntity(
            id=upr.id,
            user_id=upr.user_id,
            project_id=upr.project_id,
            role_id=upr.role_id,
            user=self._to_domain_user(upr.user) if upr.user else None,
            role=self._to_domain_role(upr.role) if upr.role else None,
            project=self._to_domain_project(
                upr.project) if upr.project else None,
            created_at=upr.created_at,
            updated_at=upr.updated_at
        )

    def _to_domain_user(self, user: User) -> UserEntity:
        return UserEntity(
            id=user.id,
            email=user.email,
            name=user.name,
            created_at=user.created_at,
            updated_at=user.updated_at
        )

    def _to_domain_role(self, role: Role) -> RoleEntity:
        return RoleEntity(
            id=role.id,
            name=role.name,
            description=role.description,
            is_system_role=role.is_system_role,
            is_active=role.is_active,
            created_at=role.created_at,
            updated_at=role.updated_at
        )

    def _to_domain_project(self, project: Project) -> ProjectEntity:
        return ProjectEntity(
            id=project.id,
            name=project.name,
            key=project.key,
            description=project.description,
            created_at=project.created_at,
            updated_at=project.updated_at
        )

    def _to_domain_project_role(self, role: Role, project: Project) -> ProjectRole:
        return ProjectRole(
            project_id=project.id,
            role_name=role.name
        )

    async def get_role_by_name(self, name: str) -> Optional[RoleEntity]:
        result = await self.session.exec(
            select(Role).where(Role.name == name)
        )
        role = result.first()
        return self._to_domain(role) if role else None

    async def get_role_permissions(self, role_id: int) -> List[PermissionEntity]:
        result = await self.session.exec(
            select(Permission)
            .join(RolePermission)
            .where(RolePermission.role_id == role_id)
        )
        permissions = result.all()
        return [self._permission_to_domain(p) for p in permissions]

    async def assign_system_role_to_user(self, user_id: int, role_name: str) -> None:
        try:
            # Get role
            role_result = await self.session.exec(
                select(Role).where(Role.name == role_name)
            )
            role = role_result.first()
            if not role:
                raise RoleNotFoundError(role_name=role_name)

            # Update user's system role
            user_result = await self.session.exec(
                select(User).where(User.id == user_id)
            )
            user = user_result.first()
            if not user:
                raise UserNotFoundError("User not found")

            user.role_id = role.id
            await self.session.commit()
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise RoleError(
                f"Failed to assign system role to user: {str(e)}") from e

    async def assign_project_role_to_user(
        self,
        user_id: int,
        project_id: int,
        role_name: str
    ) -> None:
        """Assign or update a project role for a user"""
        # Get role
        role_result = await self.session.exec(
            select(Role).where(Role.name == role_name)
        )
        role = role_result.first()
        if not role or not role.is_active or role.id is None:
            raise RoleNotFoundError(role_name=role_name)

        # Check if role is project role
        if role.is_system_role:
            raise RoleIsSystemRoleError(role_name=role_name)

        # Check if assignment already exists
        existing_assignment = await self.session.exec(
            select(UserProjectRole)
            .where(
                UserProjectRole.user_id == user_id,
                UserProjectRole.project_id == project_id
            )
        )
        assignment = existing_assignment.first()

        if assignment:
            # Update existing assignment
            assignment.role_id = role.id
            self.session.add(assignment)
        else:
            # Create new assignment
            new_assignment = UserProjectRole(
                user_id=user_id,
                project_id=project_id,
                role_id=role.id
            )
            self.session.add(new_assignment)

        await self.session.commit()

    async def get_system_role_by_user_id(self, user_id: int) -> Optional[SystemRole]:
        result = await self.session.exec(
            select(Role)
            .join(User)
            .where(User.id == user_id)
        )
        role = result.first()
        return SystemRole(role_name=role.name) if role else None

    async def get_project_roles_by_user_id(
        self,
        user_id: int,
        project_id: Optional[int] = None
    ) -> List[ProjectRole]:
        query = select(Role, Project)\
            .join(UserProjectRole, col(Role.id) == UserProjectRole.role_id)\
            .join(Project, col(Project.id) == UserProjectRole.project_id)

        if project_id:
            query = query.where(
                UserProjectRole.user_id == user_id,
                UserProjectRole.project_id == project_id
            )
        else:
            query = query.where(UserProjectRole.user_id == user_id)

        result = await self.session.exec(query)
        roles = result.all()
        return [self._to_domain_project_role(r[0], r[1]) for r in roles]

    async def get_all_roles(
        self,
        page: int = 1,
        page_size: int = 10,
        search: Optional[str] = None,
        sort_by: Optional[str] = None,
        sort_order: Optional[str] = None,
        is_active: Optional[bool] = None,
        is_system_role: Optional[bool] = None
    ) -> Tuple[List[RoleEntity], int]:
        """Get paginated, filtered and sorted roles"""
        try:
            # Base query with permissions loaded
            base_query = select(Role).options(selectinload(Role.permissions))  # type: ignore

            # Apply filters
            if is_active is not None:
                base_query = base_query.where(Role.is_active == is_active)

            if is_system_role is not None:
                base_query = base_query.where(Role.is_system_role == is_system_role)

            # Apply search
            if search:
                search_term = f"%{search}%"
                base_query = base_query.where(
                    or_(
                        Role.name.ilike(search_term),  # type: ignore
                        Role.description.ilike(search_term)  # type: ignore
                    )
                )

            # Get total count before pagination and sorting
            count_query = select(func.count()).select_from(base_query.subquery())
            total = await self.session.scalar(count_query) or 0

            # Apply sorting
            valid_sort_fields = {"name", "created_at", "updated_at", "is_active", "is_system_role"}
            if sort_by and sort_by in valid_sort_fields:
                sort_column = getattr(Role, sort_by)
                if sort_order and sort_order.lower() == "desc":
                    base_query = base_query.order_by(desc(sort_column))
                else:
                    base_query = base_query.order_by(asc(sort_column))
            else:
                # Default sorting by name
                base_query = base_query.order_by(asc(Role.name))

            # Apply pagination
            base_query = base_query.offset((page - 1) * page_size).limit(page_size)

            # Execute query
            result = await self.session.exec(base_query)
            roles = result.all()

            # Convert to domain entities
            domain_roles = [self._to_domain(role) for role in roles]

            return domain_roles, total

        except SQLAlchemyError as e:
            raise RoleError(f"Failed to fetch roles: {str(e)}") from e

    async def create_role(self, role_data: RoleCreate) -> RoleEntity:
        try:
            # Check if role already exists
            existing_role = await self.get_role_by_name(role_data.name)
            if existing_role:
                raise RoleAlreadyExistsError(role_data.name)

            # Create role
            role = Role(
                name=role_data.name,
                description=role_data.description or "",
                is_system_role=role_data.is_system_role,
                is_active=role_data.is_active
            )
            self.session.add(role)
            await self.session.commit()  # Commit to get the role.id
            await self.session.refresh(role)

            # If permission_names are provided, fetch and link permissions
            if role_data.permissions:
                # Get permissions by names using async query
                permissions_query = select(Permission).where(
                    or_(*[Permission.id ==
                        id for id in role_data.permissions])
                )
                result = await self.session.exec(permissions_query)
                permissions = result.all()
                # Validate all permissions exist
                found_ids = {p.id for p in permissions}
                missing_ids = set(role_data.permissions) - found_ids
                if missing_ids:
                    raise InvalidPermissionIdsError(list(missing_ids))

                # Create role permission associations
                role_permissions = [
                    RolePermission(
                        role_id=role.id,
                        permission_id=permission.id
                    )
                    for permission in permissions
                ]

                self.session.add_all(role_permissions)
                await self.session.commit()

            # Get fresh role data with permissions
            role_query = select(Role).where(Role.id == role.id).options(
                selectinload(Role.permissions))  # type: ignore
            role_result = await self.session.exec(role_query)
            updated_role = role_result.first()

            if not updated_role:
                raise RoleNotFoundError(role.id)

            return self._to_domain(updated_role)

        except SQLAlchemyError as e:
            await self.session.rollback()
            raise RoleCreateError(
                role_data.name, f"Failed to create role: {str(e)}") from e
        except Exception as e:
            await self.session.rollback()
            raise e from e

    async def update_role(self, role_id: int, role_data: RoleUpdate) -> RoleEntity:
        """Update role with new data including permissions"""
        try:
            # Get role with permissions loaded
            get_role_with_permissions_query = select(Role).where(Role.id == role_id).options(
                selectinload(Role.permissions))  # type: ignore
            get_role_with_permissions_result = await self.session.exec(get_role_with_permissions_query)
            role = get_role_with_permissions_result.first()

            if not role:
                raise RoleNotFoundError(role_id)

            # Update basic fields
            if role_data.name is not None:
                role.name = role_data.name
            if role_data.description is not None:
                role.description = role_data.description
            if role_data.is_active is not None:
                role.is_active = role_data.is_active
            if role_data.is_system_role is not None:
                role.is_system_role = role_data.is_system_role

            # Update permissions if provided
            if role_data.permissions is not None:
                # Get permissions by names
                get_permissions_by_names_query = select(Permission).where(
                    or_(*[Permission.id ==
                        id for id in role_data.permissions])
                )
                get_permissions_by_names_result = await self.session.exec(get_permissions_by_names_query)
                permissions = get_permissions_by_names_result.all()

                # Validate all permissions exist
                found_ids = {p.id for p in permissions}
                missing_ids = set(role_data.permissions) - found_ids
                if missing_ids:
                    raise InvalidPermissionIdsError(list(missing_ids))

                # Bugs of sqlmodel, link: https://github.com/fastapi/sqlmodel/issues/909
                # Delete existing role permissions
                delete_query = delete(RolePermission).where(
                    RolePermission.role_id == role_id  # type: ignore
                )
                await self.session.exec(delete_query)  # type: ignore

                # Create new role permissions
                role_permissions = [
                    RolePermission(
                        role_id=role.id,
                        permission_id=permission.id
                    )
                    for permission in permissions
                ]
                self.session.add_all(role_permissions)

            await self.session.commit()
            await self.session.refresh(role)

            # Get fresh role data with permissions
            get_role_by_id_query = select(Role).where(Role.id == role_id).options(
                selectinload(Role.permissions))  # type: ignore
            get_role_by_id_result = await self.session.exec(get_role_by_id_query)
            updated_role = get_role_by_id_result.first()

            if not updated_role:
                raise RoleNotFoundError(role_id)

            return self._to_domain(updated_role)
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise RoleUpdateError(
                role_data.name or str(role_id), f"Failed to update role: {str(e)}") from e
        except Exception as e:
            await self.session.rollback()
            raise e from e

    async def delete_role(self, role_id: int) -> RoleEntity:
        role = await self.session.get(Role, role_id)
        if not role:
            raise RoleNotFoundError(role_id)
        role.is_active = False
        await self.session.commit()
        await self.session.refresh(role)
        return self._to_domain(role)

    async def get_project_roles_by_project_id(
        self,
        project_id: int,
        page: int = 1,
        page_size: int = 10,
        role_name: Optional[str] = None,
        search: Optional[str] = None
    ) -> Tuple[List[UserProjectRoleEntity], int]:
        try:
            # Base query
            base_query = select(UserProjectRole)\
                .options(
                    selectinload(UserProjectRole.user),  # type: ignore
                    selectinload(UserProjectRole.role)  # type: ignore
            )\
                .where(UserProjectRole.project_id == project_id)

            # Apply role filter
            if role_name:
                base_query = base_query.join(
                    Role).where(Role.name == role_name)

            # Apply search filter
            if search:
                search_term = f"%{search}%"
                base_query = base_query.join(User).where(
                    or_(
                        User.name.ilike(search_term),  # type: ignore
                        User.email.ilike(search_term)  # type: ignore
                    )
                )

            # Get total count before pagination
            count_query = select(func.count()).select_from(
                base_query.subquery())
            total = await self.session.scalar(count_query)

            # Apply pagination
            base_query = base_query.offset(
                (page - 1) * page_size).limit(page_size)

            # Execute query
            result = await self.session.exec(base_query)
            assignments = result.all()

            # Convert to domain entities
            domain_assignments = [
                self._to_domain_user_project_role(a) for a in assignments
            ]

            return domain_assignments, total or 0

        except SQLAlchemyError as e:
            raise RoleError(
                f"Failed to fetch project roles: {str(e)}") from e

    async def get_system_roles(
        self,
        page: int = 1,
        page_size: int = 10,
        search: Optional[str] = None,
        sort_by: Optional[str] = None,
        sort_order: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> Tuple[List[RoleEntity], int]:
        try:
            # Base query
            base_query = select(Role).where(Role.is_system_role)

            # Apply filters
            if search:
                base_query = base_query.where(
                    or_(
                        Role.name.ilike(f"%{search}%"),  # type: ignore
                        Role.description.ilike(f"%{search}%")  # type: ignore
                    )
                )

            if is_active is not None:
                base_query = base_query.where(Role.is_active == is_active)

            # Get total count before pagination
            count_query = select(func.count()).select_from(
                base_query.subquery())
            total = await self.session.scalar(count_query)

            # Apply sorting
            if sort_by:
                direction = desc if sort_order == "desc" else asc
                base_query = base_query.order_by(
                    direction(getattr(Role, sort_by)))
            else:
                base_query = base_query.order_by(Role.name)

            # Apply pagination
            base_query = base_query.offset(
                (page - 1) * page_size).limit(page_size)

            # Execute query
            result = await self.session.exec(base_query)
            roles = result.all()

            return [self._to_domain(role) for role in roles], total or 0

        except SQLAlchemyError as e:
            raise RoleError(f"Failed to fetch system roles: {str(e)}") from e

    async def check_user_has_any_project_role(
        self,
        user_id: int,
        project_id: int
    ) -> bool:
        """Check if user has any role in project"""
        async with self.session as session:
            result = await session.execute(
                select(UserProjectRole)
                .where(
                    and_(
                        UserProjectRole.user_id == user_id,
                        UserProjectRole.project_id == project_id
                    )
                )
            )
            return result.scalar() is not None

    async def get_project_users_with_roles(
        self,
        project_id: int,
        search: Optional[str] = None
    ) -> List[UserProjectRoleEntity]:
        """Get all users in a project with their roles

        Args:
            project_id: The ID of the project
            search: Optional search term to filter users by name or email

        Returns:
            List of UserProjectRole objects with user and role information
        """
        query = (
            select(UserProjectRole)
            .options(
                selectinload(UserProjectRole.user),  # type: ignore
                selectinload(UserProjectRole.role)  # type: ignore
            )
            .where(UserProjectRole.project_id == project_id)
        )

        # Add search filter if provided
        if search:
            search_term = f"%{search}%"
            query = query.join(User, col(User.id) == UserProjectRole.user_id).where(
                or_(
                    col(User.name).ilike(search_term),
                    col(User.email).ilike(search_term)
                )
            )

        result = await self.session.exec(query)
        user_project_roles = result.all()

        return [self._to_domain_user_project_role(upr) for upr in user_project_roles]
