class TaskDomainError(Exception):
    """Base exception for task domain"""
    pass

class TaskStateError(TaskDomainError):
    """Raised when task state transition is invalid"""
    pass

class TaskNotFoundError(TaskDomainError):
    """Raised when task is not found"""
    pass
