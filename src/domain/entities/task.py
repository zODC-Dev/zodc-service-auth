from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from ..exceptions.task_exceptions import TaskStateError
from ..value_objects.task_priority import TaskPriority


class Task(BaseModel):
    """Task entity representing core business object"""
    id: Optional[int] = None
    title: str = Field(..., min_length=1)
    description: Optional[str] = None
    priority: TaskPriority = Field(default_factory=lambda: TaskPriority.create_medium())
    is_completed: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now())
    updated_at: Optional[datetime] = None

    def mark_as_completed(self) -> None:
        """Mark task as completed"""
        if self.is_completed:
            raise TaskStateError("Task is already completed")
        self.is_completed = True
        self.updated_at = datetime.now()

    def update_title(self, new_title: str) -> None:
        """Update task title"""
        if not new_title.strip():
            raise TaskStateError("Title cannot be empty")
        self.title = new_title.strip()
        self.updated_at = datetime.now()

    def update_description(self, new_description: Optional[str]) -> None:
        """Update task description"""
        self.description = new_description.strip() if new_description else None
        self.updated_at = datetime.now()

    def update_priority(self, new_priority: TaskPriority) -> None:
        """Update task priority"""
        self.priority = new_priority
        self.updated_at = datetime.now()

    class Config:
        validate_assignment = True  # Validates attributes on assignment
