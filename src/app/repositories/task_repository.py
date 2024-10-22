from sqlalchemy.orm import Session
from ..models.task import Task
from ..schemas.task import TaskCreate, TaskUpdate
from .base_repository import BaseRepository

class TaskRepository(BaseRepository):
    def __init__(self, db: Session):
        super().__init__(db, Task)