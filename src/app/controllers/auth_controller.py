from fastapi import HTTPException

from src.app.schemas.requests.auth import LoginEmailPasswordRequest, LoginSSOCallbackRequest, LoginSSORequest
from src.app.schemas.responses.auth import LoginSuccessResponse, LoginUrlResponse
from src.app.services.auth_service import AuthService
from src.domain.entities.auth import SSOCredentials, UserCredentials
from src.domain.exceptions.auth_exceptions import AuthenticationError


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
            token = await self.auth_service.login(credentials)
            return LoginSuccessResponse(
                access_token=token.access_token,
                token_type=token.token_type
            )
        except AuthenticationError as e:
            raise HTTPException(status_code=401, detail=str(e)) from e
        except Exception as e:
            raise HTTPException(status_code=500, detail="Authentication failed") from e

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
            token = await self.auth_service.handle_sso_callback(sso_credentials)
            return LoginSuccessResponse(
                access_token=token.access_token,
                token_type=token.token_type
            )
        except AuthenticationError as e:
            raise HTTPException(status_code=401, detail=str(e)) from e
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail="SSO authentication failed"
            ) from e
