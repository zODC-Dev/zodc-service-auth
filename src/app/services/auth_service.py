from src.app.schemas.auth import LoginPayload
from src.app.schemas.user import CreateUserPayload
from src.app.repositories.user_repository import user_repository
from passlib.context import CryptContext
import jwt
from fastapi import HTTPException
from src.configs.settings import settings
from datetime import timedelta, datetime
import requests
import ramda as R

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    async def login(payload: LoginPayload, db):
        user = await user_repository.get_user_by_email(email=payload.email, db=db)
        if not user or not pwd_context.verify(payload.password, user.password):
            return HTTPException(status_code=400, detail="Incorrect email or password")

        if not user.is_active:
            return HTTPException(status_code=400, detail="Inactive user")
        access_token = AuthService.create_access_token(data={"sub": user.email}, expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
        
        return {"access_token": access_token, "token_type": "bearer"}

    async def login_by_sso(az_access_token: str, db):
        graph_uri = "https://graph.microsoft.com/"
        tenant_id = settings.AZURE_AD_TENANT_ID
        client_id = settings.AZURE_AD_CLIENT_ID
        authority = f"https://login.microsoftonline.com/{tenant_id}/discovery/keys?appid={client_id}"
        access_token = az_access_token

        response_authority = requests.get(authority)
        if response_authority.status_code != 200:
            return HTTPException(status_code=400, detail="Error getting authority")
        public_keys = response_authority.json()
        kids = R.pluck("kid", public_keys["keys"])
        x5ts = R.pluck("x5t", public_keys["keys"])

        if access_token:
            alg = jwt.get_unverified_header(access_token)["alg"]
            at_kid = jwt.get_unverified_header(access_token)["kid"]
            at_x5t = jwt.get_unverified_header(access_token)["x5t"]
            if not(R.contains(at_kid, kids)) or not(R.contains(at_x5t, x5ts)):
                return HTTPException(status_code=400, detail="Invalid access token")
            decoded_token = jwt.decode(access_token, algorithms=[alg], options={"verify_signature": False})
            at_tenant_id = decoded_token["tid"]
            at_app_id = decoded_token["appid"]
            at_email = decoded_token["email"]
            at_full_name = decoded_token["name"]
            if not(R.equals(at_tenant_id, tenant_id)) or not(R.equals(at_app_id, client_id)):
                return HTTPException(status_code=400, detail="Invalid access token")
        
            be_access_token = AuthService.create_access_token(data={"sub": at_email}, expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))

            # Check if user exists in the database, if not, create the user
            user = await user_repository.get_user_by_email(email=at_email, db=db)
            if not user:
                create_user_payload = CreateUserPayload(email=at_email, password="password", full_name=at_full_name)
                user = await user_repository.create_user(payload=create_user_payload, db=db)

            return {"access_token": be_access_token, "token_type": "bearer"}

        return HTTPException(status_code=400, detail="Invalid access token")
        
    @staticmethod
    def create_access_token(data: dict, expires_delta: timedelta = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt
    
auth_service = AuthService()