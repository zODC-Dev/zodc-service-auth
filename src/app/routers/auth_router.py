from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from src.app.controllers.auth_controller import AuthController
from src.app.dependencies.auth import CurrentUser, get_auth_controller
from src.app.schemas.requests.auth import (
    LoginEmailPasswordRequest,
    LoginJiraCallbackRequest,
    LoginJiraRequest,
)
from src.app.schemas.responses.auth import LoginJiraSuccessResponse, LoginSuccessResponse, LoginUrlResponse

router = APIRouter()


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


@router.post("/jira", response_model=LoginUrlResponse)
async def login_by_jira(
    request: LoginJiraRequest,
    current_user: CurrentUser,
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
