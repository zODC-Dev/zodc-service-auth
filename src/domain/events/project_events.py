from typing import List, Optional

from pydantic import BaseModel


class ProjectJiraLinkedEvent(BaseModel):
    project_id: int  # id của project mới tạo trong auth service
    jira_project_id: str  # id của project trong Jira
    name: str
    key: str
    avatar_url: Optional[str] = None


class JiraUserInfo(BaseModel):
    jira_account_id: str
    email: str
    name: str


class JiraUsersResponseEvent(BaseModel):
    project_id: int
    jira_project_id: str
    users: List[JiraUserInfo]


class JiraUsersRequestEvent(BaseModel):
    """Event to request users from Jira"""
    admin_user_id: int  # user id of the user who is requesting the users
    project_id: int
    jira_project_id: str
    key: str
