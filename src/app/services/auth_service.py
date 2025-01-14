from datetime import datetime, timedelta

from src.configs.logger import log
from src.domain.constants.auth import TokenType
from src.domain.entities.auth import RefreshTokenEntity, SSOCredentials, TokenPair, UserCredentials
from src.domain.entities.user import User
from src.domain.exceptions.auth_exceptions import (
    InvalidCredentialsError,
    UserNotFoundError,
)
from src.domain.exceptions.user_exceptions import UserCreationError
from src.domain.repositories.auth_repository import IAuthRepository
from src.domain.repositories.refresh_token_repository import IRefreshTokenRepository
from src.domain.repositories.user_repository import IUserRepository
from src.domain.services.jira_sso_service import IJiraSSOService
from src.domain.services.microsoft_sso_service import IMicrosoftSSOService
from src.domain.services.redis_service import IRedisService
from src.domain.services.token_refresh_service import ITokenRefreshService
from src.domain.services.token_service import ITokenService


class AuthService:
    def __init__(
        self,
        auth_repository: IAuthRepository,
        user_repository: IUserRepository,
        token_service: ITokenService,
        microsoft_sso_service: IMicrosoftSSOService,
        jira_sso_service: IJiraSSOService,
        redis_service: IRedisService,
        refresh_token_repository: IRefreshTokenRepository,
        token_refresh_service: ITokenRefreshService
    ):
        self.auth_repository = auth_repository
        self.token_service = token_service
        self.microsoft_sso_service = microsoft_sso_service
        self.jira_sso_service = jira_sso_service
        self.user_repository = user_repository
        self.redis_service = redis_service
        self.refresh_token_repository = refresh_token_repository
        self.token_refresh_service = token_refresh_service

    async def login(self, credentials: UserCredentials) -> TokenPair:
        """Handle email/password login"""
        user = await self.auth_repository.verify_credentials(credentials)
        if not user:
            raise InvalidCredentialsError("Invalid email or password")

        if not user.is_active:
            raise InvalidCredentialsError("User is inactive")

        return await self.token_service.create_token_pair(user)

    async def login_by_microsoft(self, code_challenge: str) -> str:
        """Initialize Microsoft SSO login flow"""
        return await self.microsoft_sso_service.generate_microsoft_auth_url(code_challenge)

    async def login_by_jira(self) -> str:
        """Initialize Jira SSO login flow"""
        return await self.jira_sso_service.generate_jira_auth_url()

    async def handle_microsoft_callback(self, sso_credentials: SSOCredentials) -> TokenPair:
        try:
            """Handle Microsoft SSO callback"""
            # Get user info from SSO provider
            microsoft_info = await self.microsoft_sso_service.exchange_microsoft_code(
                sso_credentials.code,
                sso_credentials.code_verifier
            )

            # Get or create user
            user = await self.user_repository.get_user_by_email(microsoft_info.email)
            if user is None:
                user = await self.auth_repository.create_sso_user(microsoft_info)

            if user.id is None:
                raise UserCreationError("Something went wrong")

            # Store microsoft refresh token to refresh_tokens table
            await self.refresh_token_repository.create_refresh_token(
                RefreshTokenEntity(
                    user_id=user.id,
                    token=microsoft_info.refresh_token,
                    expires_at=datetime.now() + timedelta(days=30),
                    token_type=TokenType.MICROSOFT
                )
            )

            # Store microsoft access token to redis
            await self.redis_service.cache_token(
                user_id=user.id,
                access_token=microsoft_info.access_token,
                expiry=microsoft_info.expires_in,
                token_type=TokenType.MICROSOFT
            )

            # Create access token
            token_pair = await self.token_service.create_token_pair(user)

            # Schedule token refresh
            await self.token_refresh_service.schedule_token_refresh(user.id)

            return token_pair
        except Exception as e:
            log.error(f"Error handling Microsoft callback: {e}")
            raise e

    async def refresh_tokens(self, refresh_token: str) -> TokenPair:
        """Handle token refresh"""
        return await self.token_service.refresh_tokens(refresh_token)

    async def handle_jira_callback(self, code: str, user: User) -> str:
        """Handle Jira SSO callback"""
        # Get Jira tokens
        jira_info = await self.jira_sso_service.exchange_jira_code(code)

        if user.id is None:
            raise UserNotFoundError("User not found")

        # Store Jira access token in Redis
        await self.redis_service.cache_token(
            user_id=user.id,
            access_token=jira_info.access_token,
            expiry=jira_info.expires_in,
            token_type=TokenType.JIRA
        )

        # Schedule token refresh
        await self.token_refresh_service.schedule_token_refresh(user.id)

        return "success"
