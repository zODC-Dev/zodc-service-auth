from typing import List


class RoleError(Exception):
    """Base exception for role-related errors"""
    pass


class RoleNotFoundError(RoleError):
    """Raised when a role is not found"""

    def __init__(self, role_id: int = None, role_name: str = None):
        message = "Role not found"
        if role_id:
            message = f"Role with id {role_id} not found"
        elif role_name:
            message = f"Role with name '{role_name}' not found"
        super().__init__(message)


class RoleIsSystemRoleError(RoleError):
    """Raised when a role is a system role"""

    def __init__(self, role_name: str):
        super().__init__(
            f"Role '{role_name}' is a system role and cannot be assigned to a project")


class RoleAlreadyExistsError(RoleError):
    """Raised when attempting to create a role that already exists"""

    def __init__(self, role_name: str):
        super().__init__(f"Role with name '{role_name}' already exists")


class RoleCreateError(RoleError):
    """Raised when there's an error creating a role"""

    def __init__(self, role_name: str, reason: str = None):
        message = f"Cannot create role with name '{role_name}'"
        if reason:
            message += f": {reason}"
        super().__init__(message)


class RoleUpdateError(RoleError):
    """Raised when there's an error updating a role"""
    pass


class RoleDeleteError(RoleError):
    """Raised when there's an error deleting a role"""

    def __init__(self, role_id: int, reason: str = None):
        message = f"Cannot delete role with id {role_id}"
        if reason:
            message += f": {reason}"
        super().__init__(message)


class InvalidPermissionsError(RoleError):
    """Raised when invalid permissions are specified for a role"""

    def __init__(self, invalid_permissions: List[str]):
        super().__init__(
            f"The following permission names are invalid: {
                ', '.join(invalid_permissions)}"
        )


class SystemRoleModificationError(RoleError):
    """Raised when attempting to modify a system role without proper authorization"""

    def __init__(self, role_name: str):
        super().__init__(
            f"Cannot modify system role '{
                role_name}'. System roles are protected."
        )


class InvalidRoleTypeError(RoleError):
    """Exception raised when trying to use a role for the wrong purpose."""

    def __init__(self, role_name: str):
        super().__init__(
            f"Role with name '{
                role_name}' is not a system role and cannot be used for this purpose."
        )
