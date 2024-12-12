from dataclasses import dataclass
from enum import Enum


class PriorityLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

@dataclass(frozen=True)
class TaskPriority:
    """Value object representing task priority"""
    level: PriorityLevel
    color: str

    @classmethod
    def create_low(cls) -> "TaskPriority":
        return cls(PriorityLevel.LOW, "#green")

    @classmethod
    def create_medium(cls) -> "TaskPriority":
        return cls(PriorityLevel.MEDIUM, "#yellow")

    @classmethod
    def create_high(cls) -> "TaskPriority":
        return cls(PriorityLevel.HIGH, "#red")
