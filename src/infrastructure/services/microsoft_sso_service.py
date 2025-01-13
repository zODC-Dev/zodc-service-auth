from datetime import datetime
from typing import Any, Dict, cast

from aiohttp import ClientSession
import jwt

from src.configs.logger import log
from src.configs.settings import settings
from src.domain.entities.auth import MicrosoftIdentity
from src.domain.exceptions.auth_exceptions import SSOError
from src.domain.services.microsoft_sso_service import IMicrosoftSSOService


class MicrosoftSSOService(IMicrosoftSSOService):
    COMMON_TENANT = 'common'
    TOKEN_ENDPOINT = f"https://login.microsoftonline.com/{
        COMMON_TENANT}/oauth2/v2.0"
    SCOPE = "openid profile email offline_access User.Read"

    async def generate_microsoft_auth_url(self, code_challenge: str) -> str:
        """Generate Microsoft SSO authentication URL"""
        try:
            state_token = self._generate_state_token()

            auth_url = (
                f"{self.TOKEN_ENDPOINT}/authorize"
                f"?client_id={settings.CLIENT_AZURE_CLIENT_ID}"
                f"&response_type=code"
                f"&redirect_uri={settings.CLIENT_AZURE_REDIRECT_URI}"
                f"&response_mode=query"
                f"&scope={self.SCOPE}"
                f"&state={state_token}"
                f"&code_challenge={code_challenge}"
                f"&code_challenge_method=S256"
            )

            return auth_url
        except Exception as e:
            log.error(f"Failed to generate Microsoft auth URL: {str(e)}")
            raise SSOError("Failed to generate Microsoft authentication URL") from e

    async def exchange_microsoft_code(self, code: str, code_verifier: str) -> MicrosoftIdentity:
        """Exchange authorization code for Microsoft user information"""
        try:
            # Exchange code for tokens
            token_data = await self._exchange_code_for_token(code, code_verifier)

            # Validate and decode token
            user_info = self._validate_microsoft_token(token_data["id_token"])

            # Convert to domain entity
            return MicrosoftIdentity(
                email=user_info["email"],
                name=user_info.get("name"),
                access_token=token_data.get("access_token", ""),
                expires_in=token_data.get("expires_in", 3600),
                refresh_token=token_data.get("refresh_token"),
                scope=token_data.get("scope", "")
            )
        except Exception as e:
            log.error(f"Failed to exchange Microsoft code: {str(e)}")
            raise SSOError("Failed to authenticate with Microsoft") from e

    async def _exchange_code_for_token(self, code: str, code_verifier: str) -> Dict[str, Any]:
        """Exchange authorization code for tokens"""
        async with ClientSession() as session:
            async with session.post(
                f"{self.TOKEN_ENDPOINT}/token",
                data={
                    "client_id": settings.CLIENT_AZURE_CLIENT_ID,
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": settings.CLIENT_AZURE_REDIRECT_URI,
                    "code_verifier": code_verifier,
                }
            ) as response:
                data: Dict[str, Any] = await response.json()
                if "error" in data:
                    log.error(f"Token exchange failed: {
                              data.get('error_description')}")
                    raise SSOError("Failed to exchange authorization code")
                return data

    def _validate_microsoft_token(self, id_token: str) -> Dict[str, Any]:
        """Validate and decode Microsoft ID token"""
        try:
            # Note: In production, you should validate the token signature
            # This is simplified for demonstration
            data: Dict[str, Any] = jwt.decode(
                id_token,
                options={"verify_signature": False}
            )
            return data
        except jwt.InvalidTokenError as e:
            log.error(f"Invalid token: {str(e)}")
            raise SSOError("Invalid Microsoft token") from e

    def _generate_state_token(self) -> str:
        """Generate secure state token for OAuth flow"""
        return cast(str, jwt.encode(
            {
                "exp": datetime.now().timestamp() + 600,  # 10 minutes
                "iat": datetime.now().timestamp()
            },
            settings.JWT_SECRET,
            algorithm=settings.JWT_ALGORITHM
        ))
