from fastapi import APIRouter, Depends

from src.app.controllers.auth_controller import AuthController
from src.app.dependencies.auth import get_auth_controller
from src.app.schemas.requests.auth import LoginEmailPasswordRequest, LoginSSOCallbackRequest, LoginSSORequest
from src.app.schemas.responses.auth import LoginSuccessResponse, LoginUrlResponse

router = APIRouter()

@router.post("/login", response_model=LoginSuccessResponse)
async def login(
    request: LoginEmailPasswordRequest,
    controller: AuthController = Depends(get_auth_controller)
):
    """Handle login by using email password"""
    return await controller.login(request)

@router.post("/microsoft", response_model=LoginUrlResponse)
async def login_by_sso(
    request: LoginSSORequest,
    controller: AuthController = Depends(get_auth_controller)
):
    """Handle login by SSO request, return login url"""
    return await controller.login_by_sso(request)

@router.post("/microsoft/callback", response_model=LoginSuccessResponse)
async def sso_callback(
    request: LoginSSOCallbackRequest,
    controller: AuthController = Depends(get_auth_controller)
):
    """Handle microsoft SSO callback, and return application access_token"""
    return await controller.handle_sso_callback(request)
