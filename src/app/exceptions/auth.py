# app/exceptions/auth.py
from fastapi import HTTPException
from starlette import status

class AuthException:
    INVALID_CREDENTIALS = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    INACTIVE_USER = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Inactive user",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    INVALID_TOKEN = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    INVALID_TENANT = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Invalid tenant ID",
        headers={"WWW-Authenticate": "Bearer"},
    )
