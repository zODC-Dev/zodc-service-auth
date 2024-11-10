from sqlalchemy.orm import Session
from ..models.task import Task
from ..schemas.task import TaskCreate, TaskUpdate
from .base_repository import BaseRepository
from src.configs.database import get_db

class TaskRepository(BaseRepository):
    def __init__(self):
        super().__init__(Task)

task_repository = TaskRepository()