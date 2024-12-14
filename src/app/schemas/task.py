from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from src.domain.entities.task import Task


class TaskBase(BaseModel):
    """Base schema for task data"""
    title: str
    description: Optional[str] = None

class TaskCreate(TaskBase):
    """Schema for creating a task"""
    pass

class TaskUpdate(BaseModel):
    """Schema for updating a task"""
    title: Optional[str] = None
    description: Optional[str] = None
    is_completed: Optional[bool] = None

class TaskResponse(TaskBase):
    """Schema for task response"""
    id: Optional[int]
    is_completed: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

    @classmethod
    def from_domain(cls, task: "Task") -> "TaskResponse":
        return cls(
            id=task.id,
            title=task.title,
            description=task.description,
            is_completed=task.is_completed,
            created_at=task.created_at,
            updated_at=task.updated_at
        )
