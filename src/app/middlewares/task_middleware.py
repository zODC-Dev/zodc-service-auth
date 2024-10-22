from fastapi import Request, HTTPException
from ..services import task_service

async def task_owner_middleware(request: Request):
    pass