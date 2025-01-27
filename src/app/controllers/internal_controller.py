from fastapi import HTTPException

from src.app.schemas.responses.internal import TokenResponse
from src.configs.logger import log
from src.domain.exceptions.auth_exceptions import TokenError
from src.domain.services.token_service import ITokenService


class InternalController:
    def __init__(
        self,
        token_service: ITokenService
    ):
        self.token_service = token_service

    async def get_microsoft_token(self, user_id: int) -> TokenResponse:
        """Get valid Microsoft access token"""
        try:
            cached_token = await self.token_service.get_valid_microsoft_token(user_id)
            if cached_token:
                return TokenResponse(access_token=cached_token.access_token)
            else:
                raise HTTPException(status_code=401, detail="No valid Microsoft token found")
        except TokenError as e:
            raise HTTPException(status_code=401, detail=str(e)) from e
        except Exception as e:
            log.error(f"Failed to get Microsoft token: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to get Microsoft token") from e

    async def get_jira_token(self, user_id: int) -> TokenResponse:
        """Get valid Jira access token"""
        try:
            cached_token = await self.token_service.get_valid_jira_token(user_id)
            if cached_token:
                return TokenResponse(access_token=cached_token.access_token)
            else:
                raise HTTPException(status_code=401, detail="No valid Jira token found")
        except TokenError as e:
            raise HTTPException(status_code=401, detail=str(e)) from e
        except Exception as e:
            raise HTTPException(status_code=500, detail="Failed to get Jira token") from e
