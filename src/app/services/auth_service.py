from datetime import datetime, timedelta
from typing import Optional
from fastapi import HTTPException
import jwt
from aiohttp import ClientSession, ClientError
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from src.configs.settings import settings
from src.configs.logger import logger
from src.app.exceptions.auth import AuthException
from src.app.repositories.user_repository import user_repository, UserRepository
from src.app.schemas.auth import LoginPayload, TokenResponse, SSOResponse
from src.app.schemas.user import CreateUserPayloadSSO
from src.app.services.token_service import token_service, TokenService

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    def __init__(self, user_repository: UserRepository, token_service: TokenService):
        self.user_repository = user_repository
        self.token_service = token_service

    async def store_token(self, token_response: dict, db: AsyncSession):
        # Store refresh token in the database
        microsoft_id = token_response.get("id_token_claims", {}).get("oid")
        refresh_token = token_response.get("refresh_token")
        return await user_repository.update_refresh_token(microsoft_id, refresh_token, db=db)
    
    async def login(self, payload: LoginPayload, db: AsyncSession):
        try:
            user = await self.user_repository.get_user_by_email(email=payload.email, db=db)
            
            if not user or not pwd_context.verify(payload.password, user.password):
                raise AuthException.INVALID_CREDENTIALS
                
            if not user.is_active:
                raise AuthException.INACTIVE_USER
                
            access_token = self._create_access_token(data={"sub": user.email})
            return TokenResponse(access_token=access_token)
            
        except Exception as e:
            logger.error(f"Login failed: {str(e)}")
            raise AuthException.INVALID_CREDENTIALS

    async def login_by_sso(self, code_challenge: str) -> SSOResponse:
        """Generate Microsoft SSO authentication URL"""
        common_tenant = "common"
        
        try:
            auth_url = (
                f"https://login.microsoftonline.com/{common_tenant}/oauth2/v2.0/authorize"
                f"?client_id={settings.CLIENT_AZURE_CLIENT_ID}"
                f"&response_type=code"
                f"&redirect_uri={settings.CLIENT_AZURE_REDIRECT_URI}"
                f"&response_mode=query"
                f"&scope=openid profile email offline_access User.Read"
                f"&state={self._generate_state_token()}"
                f"&code_challenge={code_challenge}"
                f"&code_challenge_method=S256"
            )

            logger.info(f"Auth URL: {auth_url}")
            return SSOResponse(auth_url=auth_url)
            
        except Exception as e:
            logger.error(f"Failed to generate SSO URL: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to generate authentication URL")

    async def login_by_sso_callback(self, code: str, state: str, code_verifier: str, db: AsyncSession):
        """Handle Microsoft SSO callback"""

        try:
            # Exchange code for token
            token_data = await self._exchange_code_for_token(code=code, code_verifier=code_verifier)
            
            # Validate and decode token
            user_info = self._validate_microsoft_token(token_data["id_token"])
            
            # Create or get user
            user = await self._get_or_create_sso_user(user_info, db)

            # Cache Microsoft token in Redis
            await self.token_service._cache_token(
                user_id=user.id,
                access_token=token_data["access_token"],
                expiry=datetime.utcnow() + timedelta(seconds=token_data["expires_in"]),
            )

            # Cache refresh token if provided in database
            await self.user_repository.update_refresh_token(
                user_id=user.id,
                refresh_token=token_data.get("refresh_token"),
                db=db
            )
            
            # Generate backend token
            access_token = self._create_access_token(data={"sub": user.email})
            return TokenResponse(access_token=access_token)
            
        except ClientError as e:
            logger.error(f"Microsoft API error: {str(e)}")
            raise HTTPException(status_code=502, detail="Failed to communicate with Microsoft")
        except Exception as e:
            logger.error(f"SSO callback failed: {str(e)}")
            raise HTTPException(status_code=500, detail="Authentication failed")

    async def _exchange_code_for_token(self, code: str, code_verifier: str) -> dict:
        """Exchange authorization code for tokens"""
        async with ClientSession() as session:
            common_tenant = "common"
            async with session.post(
                f"https://login.microsoftonline.com/{common_tenant}/oauth2/v2.0/token",
                data={
                    "client_id": settings.CLIENT_AZURE_CLIENT_ID,
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": settings.CLIENT_AZURE_REDIRECT_URI,
                    "code_verifier": code_verifier,
                }
            ) as response:
                data = await response.json()
                if "error" in data:
                    logger.error(f"Token exchange failed: {data.get('error_description')}")
                    raise HTTPException(status_code=401, detail=data.get("error_description"))
                return data

    def _validate_microsoft_token(self, id_token: str) -> dict:
        """Validate and decode Microsoft ID token"""
        try:
            return jwt.decode(id_token, options={"verify_signature": False})
        except jwt.InvalidTokenError as e:
            logger.error(f"Token validation failed: {str(e)}")
            raise AuthException.INVALID_TOKEN

    async def _get_or_create_sso_user(self, user_info: dict, db: AsyncSession):
        """Get existing user or create new one from SSO data"""
        try:
            user = await self.user_repository.get_user_by_email(
                email=user_info["email"],
                db=db
            )
            
            if not user:
                user = await self.user_repository.create_user_by_sso(
                    payload=CreateUserPayloadSSO(
                        email=user_info["email"],
                        full_name=user_info["name"],
                        microsoft_id=user_info["sub"]
                    ),
                    db=db
                )
            return user
            
        except Exception as e:
            logger.error(f"User creation failed: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to create user")

    def _create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Generate BE access token

        Args:
            data (dict): data to encode
            expires_delta (Optional[timedelta], optional): expire time. Defaults to None.

        Raises:
            HTTPException: Failed to create access token

        Returns:
            str: access token
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + (
            expires_delta if expires_delta
            else timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        to_encode.update({"exp": expire})
        try:
            return jwt.encode(
                to_encode,
                settings.JWT_SECRET,
                algorithm=settings.JWT_ALGORITHM
            )
        except Exception as e:
            logger.error(f"Token creation failed: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to create access token")

    def _generate_state_token(self) -> str:
        """Generate secure state token for OAuth flow"""
        return jwt.encode(
            {"exp": datetime.utcnow() + timedelta(minutes=10)},
            settings.JWT_SECRET,
            algorithm=settings.JWT_ALGORITHM
        )
    
auth_service = AuthService(user_repository, token_service)