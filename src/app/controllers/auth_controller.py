from fastapi import HTTPException

from src.app.schemas.requests.auth import (
    LoginEmailPasswordRequest,
    LoginJiraCallbackRequest,
    LoginJiraRequest,
    LoginSSOCallbackRequest,
    LoginSSORequest,
    RefreshTokenRequest,
)
from src.app.schemas.responses.auth import (
    LoginJiraSuccessResponse,
    LoginSuccessResponse,
    LoginUrlResponse,
)
from src.app.schemas.responses.base import StandardResponse
from src.app.services.auth_service import AuthService
from src.configs.logger import log
from src.domain.entities.auth import SSOCredentials, UserCredentials
from src.domain.entities.user import User
from src.domain.exceptions.auth_exceptions import AuthenticationError, TokenError


class AuthController:
    def __init__(
        self,
        auth_service: AuthService,
    ):
        self.auth_service = auth_service

    async def login(
        self,
        request: LoginEmailPasswordRequest
    ) -> StandardResponse[LoginSuccessResponse]:
        try:
            credentials = UserCredentials(
                email=request.email,
                password=request.password
            )
            token_pair = await self.auth_service.login(credentials)
            return StandardResponse(
                message="Login successful",
                data=LoginSuccessResponse(
                    access_token=token_pair.access_token,
                    refresh_token=token_pair.refresh_token,
                    token_type=token_pair.token_type,
                    expires_in=token_pair.expires_in
                )
            )
        except AuthenticationError as e:
            raise HTTPException(status_code=401, detail=str(e)) from e
        except Exception as e:
            raise HTTPException(
                status_code=500, detail="Authentication failed") from e

    async def login_by_microsoft(
        self,
        request: LoginSSORequest
    ) -> StandardResponse[LoginUrlResponse]:
        try:
            auth_url = await self.auth_service.login_by_microsoft(
                request.code_challenge
            )
            return StandardResponse(
                message="SSO login URL retrieved successfully",
                data=LoginUrlResponse(auth_url=auth_url)
            )
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

    async def refresh_tokens(self, request: RefreshTokenRequest) -> StandardResponse[LoginSuccessResponse]:
        try:
            token_pair = await self.auth_service.refresh_tokens(request.refresh_token)
            return StandardResponse(
                message="Tokens refreshed successfully",
                data=LoginSuccessResponse(
                    access_token=token_pair.access_token,
                    refresh_token=token_pair.refresh_token,
                    token_type=token_pair.token_type,
                    expires_in=token_pair.expires_in
                )
            )
        except TokenError as e:
            raise HTTPException(
                status_code=401,
                detail={
                    "code": "SESSION_EXPIRED",
                    "message": "Your session has expired. Please login again."
                }
            ) from e

    async def handle_microsoft_callback(
        self,
        request: LoginSSOCallbackRequest,
    ) -> StandardResponse[LoginSuccessResponse]:
        """Handle Microsoft SSO callback"""
        try:
            sso_credentials = SSOCredentials(
                code=request.code,
                state=request.state,
                code_verifier=request.code_verifier
            )
            token_pair = await self.auth_service.handle_microsoft_callback(sso_credentials)

            return StandardResponse(
                message="Microsoft SSO callback handled successfully",
                data=LoginSuccessResponse(
                    access_token=token_pair.access_token,
                    refresh_token=token_pair.refresh_token,
                    token_type=token_pair.token_type,
                    expires_in=token_pair.expires_in
                )
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
    ) -> StandardResponse[LoginJiraSuccessResponse]:
        """Handle Jira SSO callback"""
        try:
            token_pair = await self.auth_service.handle_jira_callback(
                request.code,
                current_user
            )

            return StandardResponse(
                message="Jira SSO callback handled successfully",
                data=LoginJiraSuccessResponse(
                    access_token=token_pair.access_token,
                    refresh_token=token_pair.refresh_token,
                    token_type=token_pair.token_type,
                    expires_in=token_pair.expires_in
                )
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
    ) -> StandardResponse[LoginUrlResponse]:
        """Handle Jira SSO login request"""
        try:
            auth_url = await self.auth_service.login_by_jira()
            return StandardResponse(
                message="Jira SSO login request handled successfully",
                data=LoginUrlResponse(auth_url=auth_url)
            )
        except Exception as e:
            log.error(f"Failed to initiate Jira login: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to initiate Jira login"
            ) from e

    async def logout(self, current_user: User) -> StandardResponse[None]:
        """Handle user logout"""
        try:
            if current_user.id is None:
                raise HTTPException(status_code=401, detail="Invalid user")

            await self.auth_service.logout(current_user.id)
            return StandardResponse(
                message="Successfully logged out",
                data=None
            )
        except AuthenticationError as e:
            raise HTTPException(status_code=401, detail=str(e)) from e
        except Exception as e:
            log.error(f"Logout failed: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Logout failed"
            ) from e
