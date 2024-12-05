from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from msal import ConfidentialClientApplication
from sqlalchemy.ext.asyncio import AsyncSession
from src.configs.database import get_db
from src.app.schemas.auth import LoginPayload
from src.app.controllers.auth_controller import auth_controller
from src.configs.logger import logger
from src.configs.settings import settings
from pydantic import BaseModel

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class LoginBySSORequest(BaseModel):
    code_challenge: str

class LoginBySSOCallbackRequest(BaseModel):
    code: str
    state: str
    code_verifier: str

@router.post("/login")
async def login(
    payload: LoginPayload,
    db: AsyncSession = Depends(get_db)
):
    return await auth_controller.login(payload=payload, db=db)

# @router.post("/exchange-code")
# async def exchange_code(auth_code: str):
#     app = ConfidentialClientApplication(
#         settings.SERVER_AZURE_CLIENT_ID,
#         authority=f"https://login.microsoftonline.com/{settings.SERVER_AZURE_TENANT_ID}",
#         client_credential=settings.SERVER_AZURE_CLIENT_SECRET,
#     )
#         code=auth_code,
#     result = app.acquire_token_by_authorization_code(
#         scopes=["https://graph.microsoft.com/.default"],
#         redirect_uri=settings.SERVER_AZURE_REDIRECT_URI,
#     )
#     if "access_token" in result:
#         return {"access_token": result["access_token"]}
#     raise HTTPException(status_code=400, detail="Failed to exchange code")

@router.post("/microsoft")
async def login_by_sso(request: LoginBySSORequest):
    return await auth_controller.login_by_sso(code_challenge=request.code_challenge)

@router.post("/microsoft/callback")
async def login_by_sso_callback(
    request: LoginBySSOCallbackRequest,
    db: AsyncSession = Depends(get_db)
):
    return await auth_controller.login_by_sso_callback(code=request.code, state=request.state, code_verifier=request.code_verifier, db=db)
