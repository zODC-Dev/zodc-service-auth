from fastapi import APIRouter
from fastapi.security import OAuth2PasswordBearer
from src.app.schemas.auth import LoginPayload
from src.app.controllers.auth_controller import auth_controller
from src.configs.database import get_db
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@router.post("/auth/login")
async def login(payload: LoginPayload, db: AsyncSession = Depends(get_db)):
    return await auth_controller.login(payload=payload, db=db)

@router.post("/auth/login/sso")
async def login_by_sso(az_access_token: str = None, db: AsyncSession = Depends(get_db)):
    return await auth_controller.login_by_sso(az_access_token=az_access_token, db=db)