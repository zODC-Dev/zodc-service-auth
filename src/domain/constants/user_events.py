from enum import Enum


class UserEventType(Enum):
    ACCESS_TOKEN_UPDATED = "user.access_token.updated"
    REFRESH_TOKEN_UPDATED = "user.refresh_token.updated"
    USER_DEACTIVATED = "user.deactivated"
    USER_ACTIVATED = "user.activated"
    USER_UPDATED = "user.updated"
    USER_DELETED = "user.deleted"
    USER_CREATED = "user.created"
    USER_LOGOUT = "user.logout"
