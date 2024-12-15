from src.domain.entities.auth import AuthToken, SSOCredentials, UserCredentials
from src.domain.exceptions.auth_exceptions import (
    InvalidCredentialsError,
)
from src.domain.exceptions.user_exceptions import UserCreationError
from src.domain.repositories.auth_repository import IAuthRepository
from src.domain.repositories.user_repository import IUserRepository
from src.domain.services.redis_service import IRedisService
from src.domain.services.sso_service import ISSOService
from src.domain.services.token_service import ITokenService


class AuthService:
    def __init__(
        self,
        auth_repository: IAuthRepository,
        user_repository: IUserRepository,
        token_service: ITokenService,
        sso_service: ISSOService,
        redis_service: IRedisService
    ):
        self.auth_repository = auth_repository
        self.token_service = token_service
        self.sso_service = sso_service
        self.user_repository = user_repository
        self.redis_service = redis_service

    async def login(self, credentials: UserCredentials) -> AuthToken:
        """Handle email/password login"""
        user = await self.auth_repository.verify_credentials(credentials)
        if not user:
            raise InvalidCredentialsError("Invalid email or password")

        if not user.is_active:
            raise InvalidCredentialsError("User is inactive")

        return await self.token_service.create_app_token(user)

    async def login_by_sso(self, code_challenge: str) -> str:
        """Initialize SSO login flow"""
        return await self.sso_service.generate_auth_url(code_challenge)

    async def handle_sso_callback(self, sso_credentials: SSOCredentials) -> AuthToken:
        """Handle SSO callback"""
        # Get user info from SSO provider
        microsoft_info = await self.sso_service.exchange_code(
            sso_credentials.code,
            sso_credentials.code_verifier
        )

        # Get or create user
        user = await self.user_repository.get_user_by_email(microsoft_info.email)
        if user is None:
            user = await self.auth_repository.create_sso_user(microsoft_info)

        if user.id is None:
            raise UserCreationError("Something went wrong")

        # Store microsoft access token to redis
        await self.redis_service.cache_token(
            user_id=user.id,
            access_token=microsoft_info.access_token,
            expiry=microsoft_info.expires_in
        )


        # Create access token
        auth_token = await self.token_service.create_app_token(user)

        # Store refresh token if provided
        if auth_token.refresh_token:
            await self.token_service.store_app_refresh_token(
                user.id,
                auth_token.refresh_token
            )

        return auth_token
