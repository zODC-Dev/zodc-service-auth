from fastapi import HTTPException
from src.app.schemas.auth import LoginPayload
from src.app.services.auth_service import auth_service, AuthService
from sqlalchemy.ext.asyncio import AsyncSession
from src.configs.logger import logger

class AuthController:
    def __init__(self, auth_service: AuthService):
        self.auth_service = auth_service

    async def login(self, payload: LoginPayload, db: AsyncSession):
        try:
            return await self.auth_service.login(payload=payload, db=db)
        except Exception as e:
            logger.error(f"Login controller error: {str(e)}")
            raise HTTPException(status_code=500, detail="Authentication failed")

    async def login_by_sso(self, code_challenge: str):
        try:
            return await self.auth_service.login_by_sso(code_challenge=code_challenge)
        except Exception as e:
            logger.error(f"SSO login controller error: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to initiate SSO login")

    async def login_by_sso_callback(self, code: str, state: str, code_verifier: str, db: AsyncSession):
        try:
            return await self.auth_service.login_by_sso_callback(code=code, state=state, code_verifier=code_verifier, db=db)
        except Exception as e:
            logger.error(f"SSO callback controller error: {str(e)}")
            raise HTTPException(status_code=500, detail="SSO authentication failed")

auth_controller = AuthController(auth_service)
