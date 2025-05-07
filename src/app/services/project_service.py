from typing import List, Optional, Tuple

from src.app.schemas.requests.project import LinkJiraProjectRequest
from src.configs.logger import log
from src.domain.constants.nats_events import NATSPublishTopic
from src.domain.constants.roles import ProjectRoles
from src.domain.entities.project import Project, ProjectCreate, ProjectUpdate
from src.domain.entities.user import UserCreate
from src.domain.entities.user_project_role import UserProjectRole
from src.domain.events.project_events import (
    JiraProjectSyncNATSReplyDTO,
    JiraProjectSyncNATSRequestDTO,
    JiraUsersResponseEvent,
    SyncedJiraUserDTO,
)
from src.domain.exceptions.project_exceptions import (
    ProjectCreateError,
    ProjectKeyAlreadyExistsError,
    ProjectNotFoundError,
)
from src.domain.exceptions.role_exceptions import RoleNotFoundError
from src.domain.repositories.project_repository import IProjectRepository
from src.domain.repositories.role_repository import IRoleRepository
from src.domain.repositories.user_repository import IUserRepository
from src.domain.services.nats_service import INATSService


class ProjectService:
    def __init__(
        self,
        project_repository: IProjectRepository,
        role_repository: IRoleRepository,
        user_repository: IUserRepository,
        nats_service: INATSService
    ):
        self.project_repository = project_repository
        self.role_repository = role_repository
        self.user_repository = user_repository
        self.nats_service = nats_service

    async def create_project(self, project_data: ProjectCreate) -> Project:
        existing_project = await self.project_repository.get_project_by_key(project_data.key)
        if existing_project:
            raise ProjectKeyAlreadyExistsError(
                f"Project with key '{project_data.key}' already exists")
        return await self.project_repository.create_project(project_data)

    async def get_project(self, project_key: str) -> Project:
        project = await self.project_repository.get_project_by_key(project_key)
        if not project:
            raise ProjectNotFoundError(
                f"Project with key {project_key} not found")
        return project

    async def get_all_projects(self) -> List[Project]:
        return await self.project_repository.get_all_projects()

    async def update_project(self, project_id: int, project_data: ProjectUpdate) -> Project:
        project = await self.project_repository.get_project_by_id(project_id)
        if not project:
            raise ProjectNotFoundError(
                f"Project with id {project_id} not found")
        return await self.project_repository.update_project(project_id, project_data)

    async def delete_project(self, project_id: int) -> None:
        project = await self.project_repository.get_project_by_id(project_id)
        if not project:
            raise ProjectNotFoundError(
                f"Project with id {project_id} not found")
        await self.project_repository.delete_project(project_id)

    async def get_user_projects(self, user_id: int) -> List[Project]:
        return await self.project_repository.get_user_projects(user_id)

    async def link_jira_project(
        self,
        project_data: LinkJiraProjectRequest,
        current_user_id: int
    ) -> Project:
        # Check if project with key already exists
        existing_project = await self.project_repository.get_project_by_key(project_data.key)
        if existing_project:
            raise ProjectKeyAlreadyExistsError(
                f"Project with key '{project_data.key}' already exists")

        # Create new project
        new_project = await self.project_repository.create_project(
            ProjectCreate(
                key=project_data.key,
                name=project_data.name,
                description=project_data.description,
                avatar_url=project_data.avatar_url
            )
        )
        if not new_project.id:
            raise ProjectCreateError("Failed to create project")

        # Assign product owner role to current user
        await self.role_repository.assign_project_role_to_user(
            user_id=current_user_id,
            project_id=new_project.id,
            role_name=ProjectRoles.PROJECT_PRODUCT_OWNER.value
        )

        # Create Jira project sync request DTO
        sync_request = JiraProjectSyncNATSRequestDTO(
            project_id=new_project.id,
            user_id=current_user_id,
            project_key=project_data.key,
            jira_project_id=project_data.jira_project_id,
            sync_issues=True,
            sync_sprints=True,
            sync_users=True
        )

        # Publish project sync request to NATS and wait for reply
        try:
            reply_data = await self.nats_service.request(
                NATSPublishTopic.JIRA_PROJECT_SYNC.value,
                sync_request.model_dump(mode='json', exclude=None),
                timeout=300
            )

            # Process reply data
            reply = JiraProjectSyncNATSReplyDTO.model_validate(reply_data)
            if not reply.data.success:
                raise Exception(f"Jira project sync failed: {reply.data.error_message}")
            else:
                log.info(f"Jira project sync completed: Issues: {reply.data.sync_summary.synced_issues}/{reply.data.sync_summary.total_issues}, " +
                         f"Sprints: {reply.data.sync_summary.synced_sprints}/{reply.data.sync_summary.total_sprints}, " +
                         f"Users: {reply.data.sync_summary.synced_users}/{reply.data.sync_summary.total_users}")

                # Process synced users from Jira
                if reply.data.synced_users:
                    await self._process_synced_jira_users(reply.data.synced_users, new_project.id)
        except Exception as e:
            raise Exception(f"Error during Jira project sync: {str(e)}") from e

        # # Publish find users event to NATS
        # jira_event = JiraUsersRequestEvent(
        #     admin_user_id=current_user_id,
        #     project_id=new_project.id,
        #     jira_project_id=project_data.jira_project_id,
        #     key=project_data.key,
        # )
        # await self.nats_service.publish(
        #     NATSPublishTopic.JIRA_USERS_REQUEST.value,
        #     jira_event.model_dump(mode='json', exclude=None)
        # )

        return new_project

    async def _process_synced_jira_users(self, synced_users: List[SyncedJiraUserDTO], project_id: int):
        """Process synced users from Jira and create users if they don't exist.

        Args:
            synced_users: List of SyncedJiraUserDTO objects
            project_id: The ID of the project
        """
        try:
            # Get member role
            member_role = await self.role_repository.get_role_by_name(ProjectRoles.TEAM_MEMBER.value)
            if not member_role:
                raise RoleNotFoundError(role_name=ProjectRoles.TEAM_MEMBER.value)

            log.info(f"Processing {synced_users} synced users")
            for jira_user in synced_users:
                # First try to find user by email
                user = await self.user_repository.get_user_by_email(jira_user.email)

                if not user:
                    # If not found by email, try to find by Jira account ID
                    user = await self.user_repository.get_user_by_jira_account_id(jira_user.jira_account_id)

                if not user:
                    # Create new user if not exists
                    user = await self.user_repository.create_user(
                        UserCreate(
                            email=jira_user.email,
                            name=jira_user.name,
                            is_active=False,
                            jira_account_id=jira_user.jira_account_id,
                            is_jira_linked=False,
                            is_system_user=False,  # Users created from Jira sync are not system users
                            avatar_url=jira_user.avatar_url
                        )
                    )
                    log.info(f"Created new inactive user from Jira sync: {jira_user.email}")

                if user and user.id:
                    # Check if user already has a role in project
                    has_role = await self.role_repository.check_user_has_any_project_role(
                        user_id=user.id,
                        project_id=project_id
                    )

                    # Only assign member role if user doesn't have any role
                    if not has_role:
                        await self.role_repository.assign_project_role_to_user(
                            user_id=user.id,
                            project_id=project_id,
                            role_name=ProjectRoles.TEAM_MEMBER.value
                        )
                        log.info(f"Assigned member role to user {user.email} in project {project_id}")
        except Exception as e:
            log.error(f"Error processing synced Jira users: {str(e)}")
            # Don't raise exception to not interrupt the project creation flow
            # Just log the error and continue

    async def handle_jira_users_response_event(self, event: JiraUsersResponseEvent) -> None:
        """Handle users found in Jira project"""
        try:
            # Verify project exists
            project = await self.project_repository.get_project_by_id(event.project_id)
            if not project:
                raise ProjectNotFoundError(f"Project with id {event.project_id} not found")

            # Get member role
            member_role = await self.role_repository.get_role_by_name(ProjectRoles.TEAM_MEMBER.value)
            if not member_role:
                raise RoleNotFoundError(role_name=ProjectRoles.TEAM_MEMBER.value)

            # Find matching users by jira_account_id and assign member role
            for jira_user in event.users:
                # Try to find existing user
                user = await self.user_repository.get_user_by_jira_account_id(
                    jira_user.jira_account_id
                )

                if not user:
                    # Create new inactive user if not exists
                    user = await self.user_repository.create_user(
                        UserCreate(
                            email=jira_user.email,
                            name=jira_user.name,
                            is_active=False,
                            jira_account_id=jira_user.jira_account_id,
                            is_jira_linked=True,
                            is_system_user=False,  # Users created from Jira sync are not system users
                        )
                    )
                    log.info(f"Created new inactive user from Jira: {jira_user.email}")

                if user and user.id:
                    # Check if user already has a role in project
                    has_role = await self.role_repository.check_user_has_any_project_role(
                        user_id=user.id,
                        project_id=event.project_id
                    )

                    # Only assign member role if user doesn't have any role
                    if not has_role:
                        await self.role_repository.assign_project_role_to_user(
                            user_id=user.id,
                            project_id=event.project_id,
                            role_name=ProjectRoles.TEAM_MEMBER.value
                        )
                        log.info(f"Assigned member role to user {user.email} in project {event.project_id}")

        except Exception as e:
            log.error(f"Error handling Jira users found event: {str(e)}")
            raise

    async def get_project_users_with_roles(self, project_key: str, search: Optional[str] = None) -> List[UserProjectRole]:
        """Get all users in a project with their roles

        Args:
            project_key: The key of the project
            search: Optional search term to filter users by name or email

        Returns:
            List of UserProjectRole objects with user and role information
        """
        # First check if the project exists
        project = await self.project_repository.get_project_by_key(project_key)
        if not project or not project.id:
            raise ProjectNotFoundError(f"Project with key {project_key} not found")

        # Get all user_project_roles for this project with user and role information
        # This will need to be implemented in the repository
        return await self.role_repository.get_project_users_with_roles(project.id, search)

    async def get_project_users_with_roles_paginated(
        self,
        project_id: int,
        page: int = 1,
        page_size: int = 10,
        search: Optional[str] = None,
        sort_by: Optional[str] = None,
        sort_order: Optional[str] = None,
        role_id: Optional[int] = None
    ) -> Tuple[List[UserProjectRole], int]:
        """Get users in a project with their roles with pagination, filtering, searching, and sorting

        Args:
            project_id: The ID of the project
            page: Page number (starts at 1)
            page_size: Number of items per page
            search: Optional search term to filter users by name or email
            sort_by: Field to sort by (name, email, role_id)
            sort_order: Sort order (asc or desc)
            role_id: Filter by role ID

        Returns:
            Tuple containing a list of UserProjectRole objects and the total count
        """
        # First check if the project exists
        project = await self.project_repository.get_project_by_id(project_id)
        if not project:
            raise ProjectNotFoundError(f"Project with id {project_id} not found")

        # Get all user_project_roles for this project with user and role information
        # with pagination, filtering, searching, and sorting
        return await self.role_repository.get_project_users_with_roles_paginated(
            project_id=project_id,
            page=page,
            page_size=page_size,
            search=search,
            sort_by=sort_by,
            sort_order=sort_order,
            role_id=role_id
        )
