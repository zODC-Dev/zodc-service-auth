
from fastapi import HTTPException

from src.app.background.token_refresh import TokenRefreshScheduler
from src.app.schemas.requests.auth import (
    LoginEmailPasswordRequest,
    LoginJiraCallbackRequest,
    LoginJiraRequest,
    LoginSSOCallbackRequest,
    LoginSSORequest,
    RefreshTokenRequest,
)
from src.app.schemas.responses.auth import LoginJiraSuccessResponse, LoginSuccessResponse, LoginUrlResponse
from src.app.services.auth_service import AuthService
from src.configs.logger import log
from src.domain.entities.auth import SSOCredentials, UserCredentials
from src.domain.entities.user import User
from src.domain.exceptions.auth_exceptions import AuthenticationError, TokenError


class AuthController:
    def __init__(
        self,
        auth_service: AuthService,
        token_refresh_scheduler: TokenRefreshScheduler
    ):
        self.auth_service = auth_service
        self.token_refresh_scheduler = token_refresh_scheduler

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

    async def login_by_microsoft(
        self,
        request: LoginSSORequest
    ) -> LoginUrlResponse:
        try:
            log.info(f"Received Microsoft login request with code challenge: {request.code_challenge}")
            auth_url = await self.auth_service.login_by_microsoft(
                request.code_challenge
            )
            log.info(f"Generated Microsoft auth URL: {auth_url}")
            return LoginUrlResponse(auth_url=auth_url)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail="Failed to initiate SSO login"
            ) from e

    # async def handle_sso_callback(
    #     self,
    #     request: LoginSSOCallbackRequest
    # ) -> LoginSuccessResponse:
    #     try:
    #         sso_credentials = SSOCredentials(
    #             code=request.code,
    #             state=request.state,
    #             code_verifier=request.code_verifier
    #         )
    #         token_pair = await self.auth_service.handle_sso_callback(sso_credentials)
    #         return LoginSuccessResponse(
    #             access_token=token_pair.access_token,
    #             refresh_token=token_pair.refresh_token,
    #             token_type=token_pair.token_type,
    #             expires_in=token_pair.expires_in
    #         )
    #     except AuthenticationError as e:
    #         raise HTTPException(status_code=401, detail=str(e)) from e
    #     except Exception as e:
    #         raise HTTPException(
    #             status_code=500,
    #             detail="SSO authentication failed"
    #         ) from e

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

    async def handle_microsoft_callback(
        self,
        request: LoginSSOCallbackRequest,
    ) -> LoginSuccessResponse:
        """Handle Microsoft SSO callback"""
        try:
            sso_credentials = SSOCredentials(
                code=request.code,
                state=request.state,
                code_verifier=request.code_verifier
            )
            token_pair = await self.auth_service.handle_microsoft_callback(sso_credentials)

            return LoginSuccessResponse(
                access_token=token_pair.access_token,
                refresh_token=token_pair.refresh_token,
                token_type=token_pair.token_type,
                expires_in=token_pair.expires_in
            )
        except AuthenticationError as e:
            raise HTTPException(status_code=401, detail=str(e)) from e
        except Exception as e:
            log.error(f"Microsoft authentication failed: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Microsoft authentication failed"
            ) from e

    async def handle_jira_callback(
        self,
        request: LoginJiraCallbackRequest,
        current_user: User
    ) -> LoginJiraSuccessResponse:
        """Handle Jira SSO callback"""
        try:
            status = await self.auth_service.handle_jira_callback(
                request.code,
                current_user
            )

            if status == "success":
                return LoginJiraSuccessResponse(
                    status="success",
                    message="Jira authentication successful"
                )
            else:
                raise HTTPException(
                    status_code=401,
                    detail="Jira authentication failed"
                )
        except AuthenticationError as e:
            raise HTTPException(status_code=401, detail=str(e)) from e
        except Exception as e:
            log.error(f"Jira authentication failed: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Jira authentication failed"
            ) from e

    async def login_by_jira(
        self,
        request: LoginJiraRequest,
    ) -> LoginUrlResponse:
        """Handle Jira SSO login request"""
        try:
            auth_url = await self.auth_service.login_by_jira()
            return LoginUrlResponse(auth_url=auth_url)
        except Exception as e:
            log.error(f"Failed to initiate Jira login: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to initiate Jira login"
            ) from e
