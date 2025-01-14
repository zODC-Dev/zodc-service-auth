from typing import Any, Dict

from aiohttp import ClientSession

from src.configs.logger import log
from src.configs.settings import settings
from src.domain.entities.auth import JiraIdentity
from src.domain.exceptions.auth_exceptions import SSOError
from src.domain.services.jira_sso_service import IJiraSSOService


class JiraSSOService(IJiraSSOService):
    TOKEN_ENDPOINT = "https://auth.atlassian.com/oauth/token"
    SCOPE = "read:jira-user read:jira-work write:jira-work"

    async def generate_jira_auth_url(self) -> str:
        """Generate Jira SSO authentication URL"""
        try:
            auth_url = (
                "https://auth.atlassian.com/authorize"
                f"?client_id={settings.JIRA_CLIENT_ID}"
                f"&response_type=code"
                f"&redirect_uri={settings.JIRA_REDIRECT_URI}"
                f"&scope={self.SCOPE}"
                "&prompt=consent"
            )
            return auth_url
        except Exception as e:
            log.error(f"Failed to generate Jira auth URL: {str(e)}")
            raise SSOError("Failed to generate Jira authentication URL") from e

    async def exchange_jira_code(self, code: str) -> JiraIdentity:
        """Exchange authorization code for Jira tokens"""
        try:
            token_data = await self._exchange_code_for_token(code)
            return JiraIdentity(
                access_token=token_data["access_token"],
                refresh_token=token_data.get("refresh_token"),
                expires_in=token_data.get("expires_in", 3600),
                scope=token_data.get("scope", "")
            )
        except Exception as e:
            log.error(f"Failed to exchange Jira code: {str(e)}")
            raise SSOError("Failed to authenticate with Jira") from e

    async def _exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """Exchange authorization code for tokens"""
        async with ClientSession() as session:
            async with session.post(
                self.TOKEN_ENDPOINT,
                data={
                    "grant_type": "authorization_code",
                    "client_id": settings.JIRA_CLIENT_ID,
                    "client_secret": settings.JIRA_CLIENT_SECRET,
                    "code": code,
                    "redirect_uri": settings.JIRA_REDIRECT_URI,
                }
            ) as response:
                data: Dict[str, Any] = await response.json()
                if "error" in data:
                    log.error(f"Jira token exchange failed: {data.get('error_description')}")
                    raise SSOError("Failed to exchange Jira authorization code")
                return data
