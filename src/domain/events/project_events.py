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


class JiraProjectSyncSummaryDTO(BaseModel):
    total_issues: int = 0
    synced_issues: int = 0
    total_sprints: int = 0
    synced_sprints: int = 0
    total_users: int = 0
    synced_users: int = 0
    started_at: str
    completed_at: Optional[str] = None


class JiraProjectSyncNATS(BaseModel):
    success: bool
    project_key: str
    error_message: Optional[str] = None
    sync_summary: JiraProjectSyncSummaryDTO


class JiraProjectSyncNATSReplyDTO(BaseModel):
    success: bool
    data: JiraProjectSyncNATS


class JiraProjectSyncNATSRequestDTO(BaseModel):
    user_id: int
    project_key: str
    project_id: int
    jira_project_id: str
    sync_issues: bool = True
    sync_sprints: bool = True
    sync_users: bool = True
