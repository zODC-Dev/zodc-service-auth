class ProjectError(Exception):
    """Base exception for project-related errors."""
    pass


class ProjectCreateError(ProjectError):
    """Exception raised when a project creation fails."""
    pass


class ProjectNotFoundError(ProjectError):
    """Exception raised when a project is not found."""
    pass


class ProjectKeyAlreadyExistsError(ProjectError):
    """Exception raised when trying to create a project with an existing key."""
    pass


class UnauthorizedError(ProjectError):
    """Exception raised when a user is not authorized to perform an action."""
    pass
