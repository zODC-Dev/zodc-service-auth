
from fastapi import APIRouter, Depends

from src.app.controllers.auth_controller import AuthController
from src.app.dependencies.auth import get_auth_controller
from src.app.schemas.requests.auth import (
    LoginEmailPasswordRequest,
    LoginSSOCallbackRequest,
    LoginSSORequest,
    RefreshTokenRequest,
)
from src.app.schemas.responses.auth import LoginSuccessResponse, LoginUrlResponse
from src.app.schemas.responses.base import StandardResponse

router = APIRouter()


@router.post("/login", response_model=StandardResponse[LoginSuccessResponse])
async def login_by_email_password(
    request: LoginEmailPasswordRequest,
    controller: AuthController = Depends(get_auth_controller)
):
    """Handle login by using email password"""
    return await controller.login(request)


@router.post("/microsoft", response_model=StandardResponse[LoginUrlResponse])
async def login_by_microsoft(
    request: LoginSSORequest,
    controller: AuthController = Depends(get_auth_controller)
):
    """Handle login by Microsoft SSO request"""
    return await controller.login_by_microsoft(request)


@router.post("/microsoft/callback", response_model=StandardResponse[LoginSuccessResponse])
async def microsoft_callback(
    request: LoginSSOCallbackRequest,
    controller: AuthController = Depends(get_auth_controller)
):
    """Handle Microsoft SSO callback"""
    return await controller.handle_microsoft_callback(request)


@router.post("/refresh", response_model=StandardResponse[LoginSuccessResponse])
async def refresh_tokens(
    request: RefreshTokenRequest,
    controller: AuthController = Depends(get_auth_controller)
):
    """Refresh access token using refresh token"""
    return await controller.refresh_tokens(request)
