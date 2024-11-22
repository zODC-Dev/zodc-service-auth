# src/app/middlewares/auth.py
from fastapi import Depends, HTTPException 
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
import jwt
from jwt import InvalidTokenError
from src.configs.settings import settings
from src.app.repositories.user_repository import user_repository
from src.app.models.user import User
from src.configs.database import get_db
from src.configs.logger import logger

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")  # Define your token endpoint

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> User:
    """
    Extract and validate the current user from the provided JWT token.
    """
    try:
        # Decode the JWT token
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM]
        )
        email: int = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")

        # Fetch the user from the database
        user = await user_repository.get_user_by_email(email=email, db=db)
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        
        logger.info(f"User ID from token: {email}")
        return user

    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
