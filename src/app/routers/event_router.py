from fastapi import APIRouter, Header, HTTPException
from src.app.controllers.event_controller import event_controller

router = APIRouter()
@router.get("/")
async def get_events(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return await event_controller.get_events()