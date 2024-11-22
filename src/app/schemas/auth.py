from pydantic import BaseModel, EmailStr
from typing import Optional

class LoginPayload(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    
class SSOResponse(BaseModel):
    auth_url: str