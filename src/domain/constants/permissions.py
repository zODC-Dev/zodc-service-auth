from enum import Enum


class PermissionGroup(Enum):
    SYSTEM = "system"
    PROJECT = "project"
    MASTERFLOW = "masterflow"


class SystemPermissions(Enum):
    CREATE_ROLE = "system-role.create"
    VIEW_ROLE = "system-role.view"
    MANAGE_ROLE = "system-role.manage"
    MANAGE_USER = "system-user.manage"
    VIEW_USER = "system-user.view"


class ProjectPermissions(Enum):
    CREATE = "project.create"
    VIEW = "project.view"
    UPDATE = "project.update"
    DELETE = "project.delete"
    MANAGE_MEMBER = "project.manage-member"


class MasterflowPermissions(Enum):
    CREATE = "masterflow.create"
    VIEW = "masterflow.view"
    UPDATE = "masterflow.update"
    DELETE = "masterflow.delete"
