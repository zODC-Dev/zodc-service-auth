from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from src.configs.database import get_db
from src.app.schemas.auth import LoginPayload
from src.app.controllers.auth_controller import auth_controller
from src.configs.logger import logger

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@router.post("/login")
async def login(
    payload: LoginPayload,
    db: AsyncSession = Depends(get_db)
):
    return await auth_controller.login(payload=payload, db=db)

@router.post("/microsoft")
async def login_by_sso():
    return await auth_controller.login_by_sso()

@router.get("/microsoft/callback")
async def login_by_sso_callback(
    code: str,
    db: AsyncSession = Depends(get_db)
):
    return await auth_controller.login_by_sso_callback(code=code, db=db)