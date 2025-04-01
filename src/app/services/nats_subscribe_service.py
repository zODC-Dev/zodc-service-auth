from typing import Any, Awaitable, Callable, Dict

from src.app.services.project_service import ProjectService
from src.app.services.role_service import RoleService
from src.configs.logger import log
from src.domain.constants.nats_events import NATSPublishTopic, NATSSubscribeTopic
from src.domain.events.project_events import JiraUsersResponseEvent
from src.domain.events.role_events import (
    AssignProjectRoleRequest,
    AssignProjectRoleResponse,
    UnassignProjectRoleRequest,
    UnassignProjectRoleResponse,
)
from src.domain.exceptions.project_exceptions import ProjectNotFoundError
from src.domain.exceptions.role_exceptions import RoleIsSystemRoleError, RoleNotFoundError
from src.domain.exceptions.user_exceptions import UserNotFoundError
from src.domain.services.nats_service import INATSService


class NATSSubscribeService:
    def __init__(
        self,
        nats_service: INATSService,
        project_service: ProjectService,
        role_service: RoleService
    ):
        self.nats_service = nats_service
        self.project_service = project_service
        self.role_service = role_service

    async def start_nats_subscribers(self) -> None:
        """Start NATS subscribers"""
        # Subscribe to existing topics
        for event_type in NATSSubscribeTopic:
            if event_type == NATSSubscribeTopic.JIRA_USERS_RESPONSE:
                await self.nats_service.subscribe(
                    subject=event_type.value,
                    callback=self.handle_jira_users_response_event
                )

        # Subscribe to direct request topics
        await self._setup_project_role_assignment_handler()
        await self._setup_project_role_unassignment_handler()

    async def handle_jira_users_response_event(self, subject: str, data: Dict[str, Any]) -> None:
        """Route Jira users found event to project service"""
        try:
            event = JiraUsersResponseEvent.model_validate(data)
            await self.project_service.handle_jira_users_response_event(event)
        except Exception as e:
            log.error(f"Error handling Jira users found event: {str(e)}")

    async def _setup_project_role_assignment_handler(self) -> None:
        """Setup handler for project role assignment requests"""
        async def handle_assign_role_request(subject: str, data: Dict[str, Any], respond: Callable[[Dict[str, Any]], Awaitable[None]]) -> None:
            try:
                # Parse request
                request = AssignProjectRoleRequest.model_validate(data)
                log.info(f"Received project role assignment request for user {request.user_id}, " +
                         f"role {request.role_name}, project {request.project_key}")

                # Process request
                try:
                    # 1. Get project by key
                    project = await self.project_service.get_project(request.project_key)

                    if not project or not project.id:
                        raise ProjectNotFoundError(f"Project with key {request.project_key} not found")

                    # 2. Verify role exists
                    role = await self.role_service.role_repository.get_role_by_name(request.role_name)
                    if not role:
                        raise RoleNotFoundError(role_name=request.role_name)

                    # 3. Verify role is not a system role
                    if role.is_system_role:
                        raise RoleIsSystemRoleError(request.role_name)

                    # 4. Verify user exists
                    user = await self.role_service.user_repository.get_user_by_id(request.user_id)
                    if not user:
                        raise UserNotFoundError(f"User with id {request.user_id} not found")

                    # 5. Assign the role
                    await self.role_service.role_repository.assign_project_role_to_user(
                        user_id=request.user_id,
                        project_id=project.id,
                        role_name=request.role_name
                    )

                    # Create success response
                    response = AssignProjectRoleResponse(
                        success=True,
                        message=f"Successfully assigned role {request.role_name} to user {request.user_id} in project {request.project_key}",
                        user_id=request.user_id,
                        role_name=request.role_name,
                        project_key=request.project_key
                    )
                    log.info(
                        f"Successfully assigned role {request.role_name} to user {request.user_id} in project {request.project_key}")

                except ProjectNotFoundError as e:
                    response = AssignProjectRoleResponse(
                        success=False,
                        message=str(e),
                        user_id=request.user_id,
                        role_name=request.role_name,
                        project_key=request.project_key,
                        error_code="PROJECT_NOT_FOUND"
                    )
                    log.error(f"Project not found error: {str(e)}")
                except RoleNotFoundError as e:
                    response = AssignProjectRoleResponse(
                        success=False,
                        message=str(e),
                        user_id=request.user_id,
                        role_name=request.role_name,
                        project_key=request.project_key,
                        error_code="ROLE_NOT_FOUND"
                    )
                    log.error(f"Role not found error: {str(e)}")
                except RoleIsSystemRoleError as e:
                    response = AssignProjectRoleResponse(
                        success=False,
                        message=str(e),
                        user_id=request.user_id,
                        role_name=request.role_name,
                        project_key=request.project_key,
                        error_code="ROLE_IS_SYSTEM_ROLE"
                    )
                    log.error(f"Role is system role error: {str(e)}")
                except UserNotFoundError as e:
                    response = AssignProjectRoleResponse(
                        success=False,
                        message=str(e),
                        user_id=request.user_id,
                        role_name=request.role_name,
                        project_key=request.project_key,
                        error_code="USER_NOT_FOUND"
                    )
                    log.error(f"User not found error: {str(e)}")
                except Exception as e:
                    response = AssignProjectRoleResponse(
                        success=False,
                        message=f"Error assigning role: {str(e)}",
                        user_id=request.user_id,
                        role_name=request.role_name,
                        project_key=request.project_key,
                        error_code="INTERNAL_ERROR"
                    )
                    log.error(f"Error assigning role: {str(e)}")

                # Send response
                await respond(response.model_dump())

            except Exception as e:
                # If we can't even parse the request or something else fails, send a generic error
                log.error(f"Error processing project role assignment request: {str(e)}")
                error_response = {
                    "success": False,
                    "message": f"Error processing request: {str(e)}",
                    "user_id": -1,
                    "role_name": "",
                    "project_key": "",
                    "error_code": "INVALID_REQUEST"
                }
                await respond(error_response)

        # Register the handler for the request topic
        await self.nats_service.subscribe_request(
            subject=NATSPublishTopic.ASSIGN_PROJECT_ROLE_REQUEST.value,
            callback=handle_assign_role_request
        )
        log.info(
            f"Subscribed to {NATSPublishTopic.ASSIGN_PROJECT_ROLE_REQUEST.value} for project role assignment requests")

    async def _setup_project_role_unassignment_handler(self) -> None:
        """Setup handler for project role unassignment requests"""
        async def handle_unassign_role_request(subject: str, data: Dict[str, Any], respond: Callable[[Dict[str, Any]], Awaitable[None]]) -> None:
            try:
                # Parse request
                request = UnassignProjectRoleRequest.model_validate(data)
                log.info(f"Received project role unassignment request for user {request.user_id}, " +
                         f"role {request.role_name}, project {request.project_key}")

                # Process request
                try:
                    # 1. Get project by key
                    project = await self.project_service.get_project(request.project_key)

                    if not project or not project.id:
                        raise ProjectNotFoundError(f"Project with key {request.project_key} not found")

                    # 2. Verify role exists
                    role = await self.role_service.role_repository.get_role_by_name(request.role_name)
                    if not role:
                        raise RoleNotFoundError(role_name=request.role_name)

                    # 3. Verify role is not a system role
                    if role.is_system_role:
                        raise RoleIsSystemRoleError(request.role_name)

                    # 4. Verify user exists
                    user = await self.role_service.user_repository.get_user_by_id(request.user_id)
                    if not user:
                        raise UserNotFoundError(f"User with id {request.user_id} not found")

                    # 5. Unassign the role
                    await self.role_service.role_repository.unassign_project_role_from_user(
                        user_id=request.user_id,
                        project_id=project.id,
                        role_name=request.role_name
                    )

                    # Create success response
                    response = UnassignProjectRoleResponse(
                        success=True,
                        message=f"Successfully unassigned role {request.role_name} from user {request.user_id} in project {request.project_key}",
                        user_id=request.user_id,
                        role_name=request.role_name,
                        project_key=request.project_key
                    )
                    log.info(
                        f"Successfully unassigned role {request.role_name} from user {request.user_id} in project {request.project_key}")

                except ProjectNotFoundError as e:
                    response = UnassignProjectRoleResponse(
                        success=False,
                        message=str(e),
                        user_id=request.user_id,
                        role_name=request.role_name,
                        project_key=request.project_key,
                        error_code="PROJECT_NOT_FOUND"
                    )
                    log.error(f"Project not found error: {str(e)}")
                except RoleNotFoundError as e:
                    response = UnassignProjectRoleResponse(
                        success=False,
                        message=str(e),
                        user_id=request.user_id,
                        role_name=request.role_name,
                        project_key=request.project_key,
                        error_code="ROLE_NOT_FOUND"
                    )
                    log.error(f"Role not found error: {str(e)}")
                except RoleIsSystemRoleError as e:
                    response = UnassignProjectRoleResponse(
                        success=False,
                        message=str(e),
                        user_id=request.user_id,
                        role_name=request.role_name,
                        project_key=request.project_key,
                        error_code="ROLE_IS_SYSTEM_ROLE"
                    )
                    log.error(f"Role is system role error: {str(e)}")
                except UserNotFoundError as e:
                    response = UnassignProjectRoleResponse(
                        success=False,
                        message=str(e),
                        user_id=request.user_id,
                        role_name=request.role_name,
                        project_key=request.project_key,
                        error_code="USER_NOT_FOUND"
                    )
                    log.error(f"User not found error: {str(e)}")
                except Exception as e:
                    response = UnassignProjectRoleResponse(
                        success=False,
                        message=f"Error unassigning role: {str(e)}",
                        user_id=request.user_id,
                        role_name=request.role_name,
                        project_key=request.project_key,
                        error_code="INTERNAL_ERROR"
                    )
                    log.error(f"Error unassigning role: {str(e)}")

                # Send response
                await respond(response.model_dump())

            except Exception as e:
                # If we can't even parse the request or something else fails, send a generic error
                log.error(f"Error processing project role unassignment request: {str(e)}")
                error_response = {
                    "success": False,
                    "message": f"Error processing request: {str(e)}",
                    "user_id": -1,
                    "role_name": "",
                    "project_key": "",
                    "error_code": "INVALID_REQUEST"
                }
                await respond(error_response)

        # Register the handler for the request topic
        await self.nats_service.subscribe_request(
            subject=NATSPublishTopic.UNASSIGN_PROJECT_ROLE_REQUEST.value,
            callback=handle_unassign_role_request
        )
        log.info(
            f"Subscribed to {NATSPublishTopic.UNASSIGN_PROJECT_ROLE_REQUEST.value} for project role unassignment requests")
