from fastapi import APIRouter
from ..controllers.task_controller import router as task_controller_router

router = APIRouter()

router.include_router(task_controller_router, prefix="/tasks", tags=["tasks"])