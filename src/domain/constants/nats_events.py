from enum import Enum


class NATSPublishTopic(str, Enum):
    ACCESS_TOKEN_UPDATED = "user.access_token.updated"
    REFRESH_TOKEN_UPDATED = "user.refresh_token.updated"
    USER_DEACTIVATED = "user.deactivated"
    USER_ACTIVATED = "user.activated"
    USER_UPDATED = "user.updated"
    USER_DELETED = "user.deleted"
    USER_CREATED = "user.created"
    USER_LOGOUT = "user.logout"
    MICROSOFT_TOKEN_UPDATED = "auth.token.microsoft"
    JIRA_TOKEN_UPDATED = "auth.token.jira"
    PROJECT_LINKED = "project.linked"
    PROJECT_UNLINKED = "project.unlinked"
    JIRA_USERS_REQUEST = "project.users.request"
    JIRA_LOGIN = "jira.login"
    MICROSOFT_LOGIN = "microsoft.login"


class NATSSubscribeTopic(str, Enum):
    JIRA_USERS_RESPONSE = "project.users.response"
