from pydantic import BaseModel


class LoginSuccessResponse(BaseModel):
    access_token: str
    token_type: str = 'bearer'


class LoginUrlResponse(BaseModel):
    auth_url: str
