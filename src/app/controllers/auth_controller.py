from src.app.schemas.auth import LoginPayload
from src.app.services.auth_service import auth_service
from sqlalchemy.ext.asyncio import AsyncSession

class AuthController:
    async def login(self, payload: LoginPayload, db: AsyncSession):
        return await auth_service.login(payload=payload, db=db)
    
    async def login_by_sso(self, az_access_token: str, db: AsyncSession):
        return await auth_service.login_by_sso(az_access_token=az_access_token, db=db)

auth_controller = AuthController()