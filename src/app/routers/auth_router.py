from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from src.app.controllers.auth_controller import AuthController
from src.app.dependencies.auth import CurrentUser, get_auth_controller
from src.app.schemas.requests.auth import (
    LoginEmailPasswordRequest,
    LoginJiraCallbackRequest,
    LoginJiraRequest,
    LoginSSOCallbackRequest,
    LoginSSORequest,
    RefreshTokenRequest,
)
from src.app.schemas.responses.auth import LoginJiraSuccessResponse, LoginSuccessResponse, LoginUrlResponse

router = APIRouter()


@router.post("/login", response_model=LoginSuccessResponse)
async def login_by_email_password(
    request: LoginEmailPasswordRequest,
    controller: AuthController = Depends(get_auth_controller)
):
    """Handle login by using email password"""
    return await controller.login(request)


@router.post("/microsoft", response_model=LoginUrlResponse)
async def login_by_microsoft(
    request: LoginSSORequest,
    controller: AuthController = Depends(get_auth_controller)
):
    """Handle login by Microsoft SSO request"""
    return await controller.login_by_microsoft(request)


@router.post("/microsoft/callback", response_model=LoginSuccessResponse)
async def microsoft_callback(
    request: LoginSSOCallbackRequest,
    controller: AuthController = Depends(get_auth_controller)
):
    """Handle Microsoft SSO callback"""
    return await controller.handle_microsoft_callback(request)


@router.post("/token", response_model=LoginSuccessResponse)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    controller: Annotated[AuthController, Depends(get_auth_controller)]
):
    """OAuth2 compatible token login"""
    request = LoginEmailPasswordRequest(
        email=form_data.username,
        password=form_data.password
    )
    return await controller.login(request)


@router.post("/refresh", response_model=LoginSuccessResponse)
async def refresh_tokens(
    request: RefreshTokenRequest,
    controller: AuthController = Depends(get_auth_controller)
):
    """Refresh access token using refresh token"""
    return await controller.refresh_tokens(request)


@router.post("/jira", response_model=LoginUrlResponse)
async def login_by_jira(
    request: LoginJiraRequest,
    controller: AuthController = Depends(get_auth_controller)
):
    """Handle login by Jira SSO request"""
    return await controller.login_by_jira(request)


@router.post("/jira/callback", response_model=LoginJiraSuccessResponse)
async def jira_callback(
    request: LoginJiraCallbackRequest,
    current_user: CurrentUser,
    controller: AuthController = Depends(get_auth_controller)
):
    """Handle Jira SSO callback"""
    return await controller.handle_jira_callback(request, current_user)
