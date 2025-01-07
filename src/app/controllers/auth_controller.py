from fastapi import HTTPException

from src.app.schemas.requests.auth import (
    LoginEmailPasswordRequest,
    LoginSSOCallbackRequest,
    LoginSSORequest,
    RefreshTokenRequest,
)
from src.app.schemas.responses.auth import LoginSuccessResponse, LoginUrlResponse
from src.app.services.auth_service import AuthService
from src.domain.entities.auth import SSOCredentials, UserCredentials
from src.domain.exceptions.auth_exceptions import AuthenticationError, TokenError


class AuthController:
    def __init__(self, auth_service: AuthService):
        self.auth_service = auth_service

    async def login(
        self,
        request: LoginEmailPasswordRequest
    ) -> LoginSuccessResponse:
        try:
            credentials = UserCredentials(
                email=request.email,
                password=request.password
            )
            token_pair = await self.auth_service.login(credentials)
            return LoginSuccessResponse(
                access_token=token_pair.access_token,
                refresh_token=token_pair.refresh_token,
                token_type=token_pair.token_type,
                expires_in=token_pair.expires_in
            )
        except AuthenticationError as e:
            raise HTTPException(status_code=401, detail=str(e)) from e
        except Exception as e:
            raise HTTPException(
                status_code=500, detail="Authentication failed") from e

    async def login_by_sso(
        self,
        request: LoginSSORequest
    ) -> LoginUrlResponse:
        try:
            auth_url = await self.auth_service.login_by_sso(
                request.code_challenge
            )
            return LoginUrlResponse(auth_url=auth_url)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail="Failed to initiate SSO login"
            ) from e

    async def handle_sso_callback(
        self,
        request: LoginSSOCallbackRequest
    ) -> LoginSuccessResponse:
        try:
            sso_credentials = SSOCredentials(
                code=request.code,
                state=request.state,
                code_verifier=request.code_verifier
            )
            token_pair = await self.auth_service.handle_sso_callback(sso_credentials)
            return LoginSuccessResponse(
                access_token=token_pair.access_token,
                refresh_token=token_pair.refresh_token,
                token_type=token_pair.token_type,
                expires_in=token_pair.expires_in
            )
        except AuthenticationError as e:
            raise HTTPException(status_code=401, detail=str(e)) from e
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail="SSO authentication failed"
            ) from e

    async def refresh_tokens(self, request: RefreshTokenRequest) -> LoginSuccessResponse:
        try:
            token_pair = await self.auth_service.refresh_tokens(request.refresh_token)
            return LoginSuccessResponse(
                access_token=token_pair.access_token,
                refresh_token=token_pair.refresh_token,
                token_type=token_pair.token_type,
                expires_in=token_pair.expires_in
            )
        except TokenError as e:
            raise HTTPException(status_code=401, detail=str(e)) from e
