from pydantic import BaseModel


class LoginSuccessResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = 'bearer'
    expires_in: int


class LoginUrlResponse(BaseModel):
    auth_url: str
