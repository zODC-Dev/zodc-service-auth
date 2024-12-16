from enum import Enum


class SystemPermissions(str, Enum):
    MANAGE_USERS = "system.users.manage"
    MANAGE_ROLES = "system.roles.manage"
    # Add more system permissions

class ProjectPermissions(str, Enum):
    VIEW_PROJECT = "project.view"
    MANAGE_TASKS = "project.tasks.manage"
    # Add more project permissions
