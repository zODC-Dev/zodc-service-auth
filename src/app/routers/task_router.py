from typing import List

from fastapi import APIRouter, Depends, Request
from sqlmodel.ext.asyncio.session import AsyncSession

from src.app.controllers.task_controller import TaskController
from src.app.decorators.auth_decorator import require_permissions
from src.app.schemas.task import TaskCreate, TaskResponse, TaskUpdate
from src.app.services.task_service import TaskService
from src.configs.database import get_db
from src.infrastructure.repositories.sqlalchemy_task_repository import SQLAlchemyTaskRepository

router = APIRouter()

def get_task_controller(db: AsyncSession = Depends(get_db)) -> TaskController:
    """Dependencies Injection for task controller"""
    repository = SQLAlchemyTaskRepository(db)
    service = TaskService(repository)
    return TaskController(service)

@router.post("/", response_model=TaskResponse)
async def create_task(
    task: TaskCreate,
    controller: TaskController = Depends(get_task_controller)
):
    """Create new task"""
    return await controller.create_task(task)

@router.get("/protected")
@require_permissions(
    system_roles=["admin"]
)
async def protected_route(request: Request):
    """Test protected route"""
    return {"message": "You have access!"}

@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    controller: TaskController = Depends(get_task_controller)
):
    """Get task by id"""
    return await controller.get_task(task_id)

@router.get("/", response_model=List[TaskResponse])
async def get_tasks(
    skip: int = 0,
    limit: int = 100,
    controller: TaskController = Depends(get_task_controller)
):
    """Get all tasks with skip and limit parameters"""
    return await controller.get_tasks(skip, limit)

@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task: TaskUpdate,
    controller: TaskController = Depends(get_task_controller)
):
    """Update task by id"""
    return await controller.update_task(task_id, task)

@router.delete("/{task_id}", response_model=TaskResponse)
async def delete_task(
    task_id: int,
    controller: TaskController = Depends(get_task_controller)
):
    """Delete task by id"""
    return await controller.delete_task(task_id)
