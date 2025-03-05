import base64
import json
from typing import Optional

from aiohttp import ClientSession

from src.configs.logger import log
from src.configs.settings import settings
from src.domain.constants.auth import TokenType
from src.domain.constants.nats_events import NATSPublishTopic
from src.domain.entities.auth import SSOCredentials, TokenPair, UserCredentials
from src.domain.entities.user import User, UserUpdate
from src.domain.exceptions.auth_exceptions import (
    AuthenticationError,
    InvalidCredentialsError,
    TokenError,
    UserNotFoundError,
)
from src.domain.exceptions.user_exceptions import UserCreationError
from src.domain.repositories.auth_repository import IAuthRepository
from src.domain.repositories.refresh_token_repository import IRefreshTokenRepository
from src.domain.repositories.user_repository import IUserRepository
from src.domain.services.jira_sso_service import IJiraSSOService
from src.domain.services.microsoft_sso_service import IMicrosoftSSOService
from src.domain.services.nats_service import INATSService
from src.domain.services.redis_service import IRedisService
from src.domain.services.token_service import ITokenService
from src.domain.services.user_event_service import IUserEventService


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
        user_event_service: IUserEventService,
        nats_service: INATSService
    ):
        self.auth_repository = auth_repository
        self.token_service = token_service
        self.microsoft_sso_service = microsoft_sso_service
        self.jira_sso_service = jira_sso_service
        self.user_repository = user_repository
        self.redis_service = redis_service
        self.refresh_token_repository = refresh_token_repository
        self.user_event_service = user_event_service
        self.nats_service = nats_service

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

            # # Publish Microsoft token event to NATS
            # token_event = TokenEvent(
            #     user_id=user.id,
            #     access_token=microsoft_info.access_token,
            #     refresh_token=microsoft_info.refresh_token,
            #     expires_in=microsoft_info.expires_in,
            #     token_type=TokenType.MICROSOFT,
            #     created_at=datetime.now(timezone.utc),
            #     expires_at=datetime.now(timezone.utc) + timedelta(seconds=microsoft_info.expires_in)
            # )
            # Publish Microsoft login event
            microsoft_login_event = {
                "user_id": user.id,
                "email": user.email,
                "access_token": microsoft_info.access_token,
                "refresh_token": microsoft_info.refresh_token,
                "expires_in": microsoft_info.expires_in,
            }

            # # Publish Microsoft token event to NATS
            # await self.nats_service.publish(
            #     NATSPublishTopic.MICROSOFT_TOKEN_UPDATED.value,
            #     token_event.model_dump(mode='json', exclude_none=True)
            # )

            # Publish Microsoft login event to NATS
            await self.nats_service.publish(
                NATSPublishTopic.MICROSOFT_LOGIN.value,
                microsoft_login_event
            )

            # Create access token
            return await self.token_service.create_token_pair(user)

        except Exception as e:
            log.error(f"Error handling Microsoft callback: {e}")
            raise e

    async def handle_jira_callback(self, code: str, user: User) -> TokenPair:
        """Handle Jira SSO callback"""
        try:
            # Get Jira tokens
            jira_info = await self.jira_sso_service.exchange_jira_code(code)

            if user.id is None:
                raise UserNotFoundError("User not found")

            # Extract Jira account ID from access token
            jira_account_id = await self._extract_jira_account_id(jira_info.access_token)

            # Fetch user avatar URL from Jira API
            avatar_url = await self._fetch_jira_user_avatar(jira_info.access_token, jira_account_id)

            # Update user with Jira account ID, linked status, and avatar URL
            await self.user_repository.update_user_by_id(
                user.id,
                UserUpdate(
                    jira_account_id=jira_account_id,
                    is_jira_linked=True,
                    avatar_url=avatar_url
                )
            )

            # Publish Jira token event to NATS
            # token_event = TokenEvent(
            #     user_id=user.id,
            #     access_token=jira_info.access_token,
            #     refresh_token=jira_info.refresh_token,
            #     expires_at=datetime.now(timezone.utc) + timedelta(seconds=jira_info.expires_in),
            #     expires_in=jira_info.expires_in,
            #     token_type=TokenType.JIRA,
            #     created_at=datetime.now(timezone.utc)
            # )
            # await self.nats_service.publish(
            #     NATSPublishTopic.JIRA_TOKEN_UPDATED.value,
            #     token_event.model_dump(mode='json', exclude_none=True)
            # )

            # Publish Jira login event
            jira_login_event = {
                "user_id": user.id,
                "jira_account_id": jira_account_id,
                "email": user.email,
                "access_token": jira_info.access_token,
                "refresh_token": jira_info.refresh_token,
                "expires_in": jira_info.expires_in,
            }
            await self.nats_service.publish(
                NATSPublishTopic.JIRA_LOGIN.value,
                jira_login_event
            )

            # Get updated user to generate new tokens
            updated_user = await self.user_repository.get_user_by_id(user.id)
            if not updated_user:
                raise UserNotFoundError("User not found after update")

            # Generate new token pair with updated is_jira_linked status
            return await self.token_service.create_token_pair(updated_user)

        except Exception as e:
            log.error(f"Error handling Jira callback: {e}")
            raise e

    async def _extract_jira_account_id(self, access_token: str) -> str:
        """Extract Jira account ID from access token"""
        try:
            # Split token and get payload part
            payload = access_token.split('.')[1]
            # Add padding if needed
            payload += '=' * (-len(payload) % 4)
            # Decode base64
            decoded = base64.b64decode(payload)
            # Parse JSON
            token_data = json.loads(decoded)
            # Get sub claim which contains account ID
            account_id: str = token_data.get('sub')

            if not account_id:
                raise ValueError("No account ID found in token")

            return account_id
        except Exception as e:
            log.error(f"Error extracting Jira account ID: {e}")
            raise ValueError("Failed to extract Jira account ID from token") from e

    async def _fetch_jira_user_avatar(self, access_token: str, account_id: str) -> Optional[str]:
        """Fetch user avatar URL from Jira API"""
        try:
            # Jira API endpoint to get user information
            url = f"{settings.JIRA_BASE_URL}/rest/api/3/user"

            # Set up headers with access token
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/json"
            }

            # Make request to Jira API
            async with ClientSession() as session:
                async with session.get(url, headers=headers, params={"accountId": account_id}) as response:
                    if response.status == 200:
                        user_data = await response.json()
                        # Extract avatar URL from response
                        if user_data and "avatarUrls" in user_data and "48x48" in user_data["avatarUrls"]:
                            return str(user_data["avatarUrls"]["48x48"])
                        return None
                    else:
                        log.error(f"Failed to fetch Jira user avatar: {response.status}")
                        return None
        except Exception as e:
            log.error(f"Error fetching Jira user avatar: {e}")
            return None

    async def logout(self, user_id: int) -> None:
        """Handle user logout"""
        try:
            await self.refresh_token_repository.revoke_tokens_by_user_and_type(
                user_id=user_id,
                token_type=TokenType.APP
            )

            await self.redis_service.delete(f"user:{user_id}")

            # Clear permission cache
            await self.redis_service.delete(f"permissions:user:{user_id}")

            # Send logout event
            await self.user_event_service.publish_user_event(
                user_id=user_id,
                event_type=NATSPublishTopic.USER_LOGOUT
            )

        except Exception as e:
            log.error(f"Error during logout: {e}")
            raise AuthenticationError("Logout failed") from e

    async def refresh_tokens(self, refresh_token: str) -> TokenPair:
        """Handle token refresh"""
        try:
            return await self.token_service.refresh_tokens(refresh_token)
        except TokenError as e:
            # If refresh token is invalid, perform logout
            try:
                # Extract user ID from the invalid refresh token
                token_data = await self.refresh_token_repository.get_by_token(refresh_token)
                if token_data and token_data.user_id:
                    await self.logout(token_data.user_id)
            except Exception as logout_error:
                log.error(f"Error during auto-logout: {logout_error}")
            raise e
