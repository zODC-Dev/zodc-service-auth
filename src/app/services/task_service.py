from ..repositories.task_repository import TaskRepository
from ..schemas.task import TaskCreate, TaskUpdate
from sqlalchemy.orm import Session

class TaskService:
    def __init__(self, db: Session):
        self.repository = TaskRepository(db)

    def create_task(self, task: TaskCreate):
        return self.repository.create(task)

    def get_task(self, task_id: int):
        return self.repository.get(task_id)

    def get_tasks(self, skip: int = 0, limit: int = 100):
        return self.repository.get_all(skip, limit)

    def update_task(self, task_id: int, task: TaskUpdate):
        return self.repository.update(task_id, task)

    def delete_task(self, task_id: int):
        return self.repository.delete(task_id)

    # Add any additional business logic methods here
    def mark_task_as_completed(self, task_id: int):
        task = self.repository.get(task_id)
        if task:
            task.is_completed = True
            return self.repository.update(task_id, TaskUpdate(is_completed=True))
        return None
