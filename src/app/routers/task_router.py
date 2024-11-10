from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from typing import List

from ..controllers.task_controller import task_controller
from ..schemas.task import Task, TaskCreate, TaskUpdate
from src.configs.database import get_db

router = APIRouter()

@router.post("/", response_model=Task)
async def create_task(task: TaskCreate, db: AsyncSession = Depends(get_db)):
    return await task_controller.create_task(task=task, db=db)

@router.get("/{task_id}", response_model=Task)
def read_task(task_id: int, db: Session = Depends(get_db)):
    return task_controller.read_task(task_id=task_id, db=db)

@router.get("/", response_model=List[Task])
async def read_tasks(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    return await task_controller.read_tasks(skip=skip, limit=limit, db=db)

@router.put("/{task_id}", response_model=Task)
async def update_task(task_id: int, task: TaskUpdate, db: AsyncSession = Depends(get_db)):
    return await task_controller.update_task(task_id=task_id, task=task, db=db)

@router.delete("/{task_id}", response_model=Task)
async def delete_task(task_id: int, db: AsyncSession = Depends(get_db)):
    return await task_controller.delete_task(task_id=task_id, db=db)