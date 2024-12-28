from typing import List, Optional, Tuple

from sqlalchemy.orm import selectinload
from sqlmodel import func, or_, select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.domain.entities.permission import Permission as PermissionEntity
from src.domain.entities.project import Project as ProjectEntity
from src.domain.entities.role import Role as RoleEntity, RoleCreate, RoleUpdate
from src.domain.entities.user import User as UserEntity
from src.domain.entities.user_project_role import UserProjectRole as UserProjectRoleEntity
from src.domain.exceptions.role_exceptions import RoleAlreadyExistsError, RoleNotFoundError
from src.domain.repositories.role_repository import IRoleRepository
from src.infrastructure.models.permission import Permission
from src.infrastructure.models.project import Project
from src.infrastructure.models.role import Role
from src.infrastructure.models.role_permission import RolePermission
from src.infrastructure.models.user import User
from src.infrastructure.models.user_project_role import UserProjectRole


class SQLAlchemyRoleRepository(IRoleRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

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
        # Get role
        role_result = await self.session.exec(
            select(Role).where(Role.name == role_name)
        )
        role = role_result.first()
        if not role:
            raise ValueError(f"Role {role_name} not found")

        # Update user's system role
        user_result = await self.session.exec(
            select(User).where(User.id == user_id)
        )
        user = user_result.first()
        if not user:
            raise ValueError(f"User {user_id} not found")

        user.role_id = role.id
        await self.session.commit()

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

    async def get_user_system_role(self, user_id: int) -> Optional[RoleEntity]:
        result = await self.session.exec(
            select(Role)
            .join(User)
            .where(User.id == user_id)
        )
        role = result.first()
        return self._to_domain(role) if role else None

    async def get_user_project_roles(
        self,
        user_id: int,
        project_id: Optional[int] = None
    ) -> List[RoleEntity]:
        query = select(Role).join(UserProjectRole)

        if project_id:
            query = query.where(
                UserProjectRole.user_id == user_id,
                UserProjectRole.project_id == project_id
            )
        else:
            query = query.where(UserProjectRole.user_id == user_id)

        result = await self.session.exec(query)
        roles = result.all()
        return [self._to_domain(r) for r in roles]

    async def get_user_permissions(
        self,
        user_id: int,
        project_id: Optional[int] = None
    ) -> List[PermissionEntity]:
        if project_id:
            # Execute queries separately and combine results in Python
            # Get system permissions
            system_perms = await self.session.exec(
                select(Permission)
                .join(RolePermission)
                .join(Role)
                .join(User)
                .where(User.id == user_id)
            )

            # Get project permissions
            project_perms = await self.session.exec(
                select(Permission)
                .join(RolePermission)
                .join(Role)
                .join(UserProjectRole)
                .where(
                    UserProjectRole.user_id == user_id,
                    UserProjectRole.project_id == project_id
                )
            )

            # Convert to lists before combining
            permissions = list(system_perms.all()) + list(project_perms.all())
            # Remove duplicates if needed
            unique_permissions = list({p.id: p for p in permissions}.values())
            return [self._permission_to_domain(p) for p in unique_permissions]
        else:
            # Just get system permissions
            result = await self.session.exec(
                select(Permission)
                .join(RolePermission)
                .join(Role)
                .join(User)
                .where(User.id == user_id)
            )
            permissions = list(result.all())
            return [self._permission_to_domain(p) for p in permissions]

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

    def _permission_to_domain(self, permission: Permission) -> PermissionEntity:
        return PermissionEntity(
            id=permission.id,
            name=permission.name,
            description=permission.description
        )

    async def get_all_roles(self, include_deleted: bool = False) -> List[RoleEntity]:
        query = select(Role)
        if not include_deleted:
            query = query.where(Role.is_active)
        result = await self.session.exec(query)
        roles = result.all()
        return [self._to_domain(r) for r in roles]

    async def create_role(self, role_data: RoleCreate) -> RoleEntity:
        # Check if role already exists
        existing_role = await self.get_role_by_name(role_data.name)
        if existing_role:
            raise RoleAlreadyExistsError(role_data.name)

        # Create role without permissions first
        role = Role(
            name=role_data.name,
            description=role_data.description or "",
            is_system_role=role_data.is_system_role,
            is_active=role_data.is_active
        )
        self.session.add(role)

        # If permission_names are provided, fetch and link permissions
        if role_data.permission_names:
            # Get permissions by names
            permissions_query = select(Permission).where(
                or_(*[Permission.name == name for name in role_data.permission_names])
            )
            result = await self.session.exec(permissions_query)
            permissions = result.all()

            # Link permissions to role
            role.permissions = list(permissions)

        await self.session.commit()
        await self.session.refresh(role)
        return self._to_domain(role)

    async def update_role(self, role_id: int, role_data: RoleUpdate) -> RoleEntity:
        role = await self.session.get(Role, role_id)
        if not role:
            raise RoleNotFoundError(role_id)

        if role_data.name is not None:
            role.name = role_data.name
        if role_data.description is not None:
            role.description = role_data.description
        if role_data.is_active is not None:
            role.is_active = role_data.is_active
        if role_data.permission_names is not None:
            # Get permissions by names
            permissions_query = select(Permission).where(
                or_(*[Permission.name == name for name in role_data.permission_names])
            )
            result = await self.session.exec(permissions_query)
            permissions = result.all()

            # Update role permissions
            role.permissions = list(permissions)

        await self.session.commit()
        await self.session.refresh(role)
        return self._to_domain(role)

    async def delete_role(self, role_id: int) -> None:
        role = await self.session.get(Role, role_id)
        if not role:
            raise RoleNotFoundError(role_id)
        role.is_active = False
        await self.session.commit()

    async def get_all_users_with_roles(self) -> List[UserEntity]:
        """Get all users with their system roles and project roles"""
        result = await self.session.exec(
            select(User)
            .options(
                selectinload(User.system_role),  # type: ignore
                selectinload(User.user_project_roles)  # type: ignore
                .selectinload(UserProjectRole.project),  # type: ignore
                selectinload(User.user_project_roles)  # type: ignore
                .selectinload(UserProjectRole.role)  # type: ignore
            )
        )
        users = result.all()
        return [self._user_to_domain(u) for u in users]

    def _user_to_domain(self, user: User) -> UserEntity:
        """Convert SQLAlchemy User model to domain entity"""
        project_roles = []
        for upr in user.user_project_roles:
            if upr.project and upr.role:
                project_roles.append({
                    "project_name": upr.project.name,
                    "role_name": upr.role.name
                })

        return UserEntity(
            id=user.id,
            email=user.email,
            name=user.name or "",
            system_role=user.system_role.name if user.system_role else None,
            project_roles=project_roles
        )

    async def get_project_role_assignments(
        self,
        project_id: int,
        page: int = 1,
        page_size: int = 10,
        role_name: Optional[str] = None,
        search: Optional[str] = None
    ) -> Tuple[List[UserProjectRoleEntity], int]:
        """Get paginated and filtered user role assignments for a project"""
        query = select(UserProjectRole)\
            .options(
                selectinload(UserProjectRole.user),  # type: ignore
                selectinload(UserProjectRole.role)  # type: ignore
        )\
            .where(UserProjectRole.project_id == project_id)

        # Apply role filter
        if role_name:
            query = query.join(Role).where(Role.name == role_name)

        # Apply search filter
        if search:
            search_term = f"%{search}%"
            query = query.join(User).where(
                or_(
                    User.name.ilike(search_term),  # type: ignore
                    User.email.ilike(search_term)  # type: ignore
                )
            )

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total = await self.session.scalar(count_query)
        if total is None:
            total = 0

        # Apply pagination
        query = query.offset((page - 1) * page_size).limit(page_size)

        # Execute query
        result = await self.session.exec(query)
        assignments = list(result.all())

        # Convert to domain entities
        domain_assignments = [
            self._to_domain_user_project_role(a) for a in assignments]

        return domain_assignments, total

    async def get_project_by_id(self, project_id: int) -> Optional[ProjectEntity]:
        query = select(Project).where(Project.id == project_id)
        result = await self.session.exec(query)
        project = result.first()
        return self._to_domain_project(project) if project else None

    async def get_user_by_id(self, user_id: int) -> Optional[UserEntity]:
        query = select(User).where(User.id == user_id)
        result = await self.session.exec(query)
        user = result.first()
        return self._to_domain_user(user) if user else None

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
