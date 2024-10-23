from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from src.configs.database import get_db
from ..schemas.task import Task, TaskCreate, TaskUpdate
from ..services import task_service

router = APIRouter()

@router.post("/", response_model=Task)
async def create_task(task: TaskCreate, db: AsyncSession = Depends(get_db)):
    return task_service.create_task(db=db, task=task)

@router.get("/{task_id}", response_model=Task)
def read_task(task_id: int, db: Session = Depends(get_db)):
    db_task = task_service.get_task(db, task_id=task_id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task

@router.get("/", response_model=List[Task])
async def read_tasks(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    tasks = await task_service.get_tasks(db, skip=skip, limit=limit)
    return tasks

@router.put("/{task_id}", response_model=Task)
async def update_task(task_id: int, task: TaskUpdate, db: AsyncSession = Depends(get_db)):
    db_task = await task_service.update_task(db, task_id=task_id, task=task)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task

@router.delete("/{task_id}", response_model=Task)
async def delete_task(task_id: int, db: AsyncSession = Depends(get_db)):
    db_task = await task_service.delete_task(db, task_id=task_id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task