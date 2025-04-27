from datetime import datetime
from typing import Any, Dict, List, Optional

from src.app.schemas.responses.base import BaseResponse
from src.domain.entities.user import User
from src.domain.entities.user_project_role import UserProjectRole


# Add new model for project roles
class ProjectRoleInfo(BaseResponse):
    project_key: str
    roles: List[str]
    permission_names: List[str]


class UserWithProfileResponse(BaseResponse):
    id: int
    email: str
    name: Optional[str]
    system_role: Optional[str] = None
    is_active: bool
    created_at: datetime
    is_jira_linked: bool
    is_system_user: bool
    permission_names: List[str]
    project_roles: List[ProjectRoleInfo] = []
    avatar_url: Optional[str] = None
    # Additional profile fields
    job_title: Optional[str] = None
    location: Optional[str] = None
    phone_number: Optional[str] = None
    joined_date: Optional[datetime] = None
    primary_skills: List[Any] = []
    secondary_skills: List[Any] = []
    education: str = ''
    certifications: str = ''

    @classmethod
    def from_domain(cls, user: User) -> "UserWithProfileResponse":
        # Create a map to group roles by project
        project_roles_map: Dict[str, Any] = {}

        if user.user_project_roles:
            for upr in user.user_project_roles:
                if upr.project and upr.role:
                    project_key = upr.project.key
                    if project_key not in project_roles_map:
                        project_roles_map[project_key] = {
                            "roles": [],
                            "permission_names": set()
                        }

                    # Add role name
                    project_roles_map[project_key]["roles"].append(upr.role.name)

                    # Add permissions from this role
                    if upr.role.permissions:
                        project_roles_map[project_key]["permission_names"].update(
                            p.name for p in upr.role.permissions
                        )

        # Convert map to list of ProjectRoleInfo
        project_roles = [
            ProjectRoleInfo(
                project_key=project_key,
                roles=info["roles"],
                permission_names=list(info["permission_names"])
            )
            for project_key, info in project_roles_map.items()
        ]

        # Extract profile data from JSONB
        profile_data = user.profile_data or {}
        primary_skills = []
        secondary_skills = []
        education = ''
        certifications = ''

        # Parse skills
        if profile_data.get("primary_skills"):
            primary_skills = profile_data.get("primary_skills", [])

        if profile_data.get("secondary_skills"):
            secondary_skills = profile_data.get("secondary_skills", [])

        # Parse education
        if profile_data.get("education"):
            education = profile_data.get("education", '')

        # Parse certifications
        if profile_data.get("certifications"):
            certifications = profile_data.get("certifications", '')

        return cls(
            id=user.id,
            email=user.email,
            name=user.name,
            system_role=user.system_role.description if user.system_role else None,
            is_active=user.is_active,
            created_at=user.created_at,
            is_jira_linked=user.is_jira_linked,
            is_system_user=user.is_system_user,
            permission_names=[
                p.name for p in user.system_role.permissions
            ] if user.system_role and user.system_role.permissions else [],
            project_roles=project_roles,
            avatar_url=user.avatar_url,
            job_title=user.job_title,
            location=user.location,
            phone_number=user.phone_number,
            joined_date=user.joined_date,
            primary_skills=primary_skills,
            secondary_skills=secondary_skills,
            education=education,
            certifications=certifications
        )


class UserResponse(BaseResponse):
    id: int
    email: str
    name: Optional[str]
    system_role: Optional[str] = None
    is_active: bool
    created_at: datetime
    is_jira_linked: bool
    is_system_user: bool
    permission_names: List[str]
    project_roles: List[ProjectRoleInfo] = []
    avatar_url: Optional[str] = None

    @classmethod
    def from_domain(cls, user: User) -> "UserResponse":
        # Create a map to group roles by project
        project_roles_map: Dict[str, Any] = {}

        if user.user_project_roles:
            for upr in user.user_project_roles:
                if upr.project and upr.role:
                    project_key = upr.project.key
                    if project_key not in project_roles_map:
                        project_roles_map[project_key] = {
                            "roles": [],
                            "permission_names": set()
                        }

                    # Add role name
                    project_roles_map[project_key]["roles"].append(upr.role.name)

                    # Add permissions from this role
                    if upr.role.permissions:
                        project_roles_map[project_key]["permission_names"].update(
                            p.name for p in upr.role.permissions
                        )

        # Convert map to list of ProjectRoleInfo
        project_roles = [
            ProjectRoleInfo(
                project_key=project_key,
                roles=info["roles"],
                permission_names=list(info["permission_names"])
            )
            for project_key, info in project_roles_map.items()
        ]

        return cls(
            id=user.id,
            email=user.email,
            name=user.name,
            system_role=user.system_role.description if user.system_role else None,
            is_active=user.is_active,
            created_at=user.created_at,
            is_jira_linked=user.is_jira_linked,
            is_system_user=user.is_system_user,
            permission_names=[
                p.name for p in user.system_role.permissions
            ] if user.system_role and user.system_role.permissions else [],
            project_roles=project_roles,
            avatar_url=user.avatar_url,
        )


class AdminUserResponse(BaseResponse):
    id: int
    name: str
    email: str
    is_system_user: bool
    avatar_url: Optional[str] = None
    system_role: Optional[str] = None
    is_active: bool
    is_jira_linked: bool

    @classmethod
    def from_domain(cls, user_project_role: UserProjectRole) -> 'AdminUserResponse':
        return cls(
            id=user_project_role.user.id if user_project_role.user else None,
            name=user_project_role.user.name if user_project_role.user else None,
            email=user_project_role.user.email if user_project_role.user else None,
            is_system_user=user_project_role.user.is_system_user if user_project_role.user else None,
            avatar_url=user_project_role.user.avatar_url if user_project_role.user else None,
            system_role=user_project_role.role.name if user_project_role.role else None,
            is_active=user_project_role.user.is_active if user_project_role.user else None,
            is_jira_linked=user_project_role.user.is_jira_linked if user_project_role.user else None,
        )

    @classmethod
    def from_user(cls, user: User) -> 'AdminUserResponse':
        return cls(
            id=user.id,
            name=user.name,
            email=user.email,
            is_system_user=user.is_system_user,
            avatar_url=user.avatar_url,
            system_role=user.system_role.name if user.system_role else None,
            is_active=user.is_active,
            is_jira_linked=user.is_jira_linked,
        )
