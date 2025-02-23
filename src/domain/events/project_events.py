from datetime import datetime
from typing import List

from pydantic import BaseModel


class ProjectJiraLinkedEvent(BaseModel):
    project_id: int  # id của project mới tạo trong auth service
    jira_project_id: str  # id của project trong Jira
    created_by: int  # user_id
    created_at: datetime


class JiraUserInfo(BaseModel):
    jira_account_id: str
    email: str
    name: str


class JiraUsersFoundEvent(BaseModel):
    project_id: int
    jira_project_id: str
    users: List[JiraUserInfo]
    created_at: datetime
