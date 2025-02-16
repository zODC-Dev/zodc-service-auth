from src.app.schemas.responses.base import BaseResponse


class LoginSuccessResponse(BaseResponse):
    access_token: str
    refresh_token: str
    token_type: str = 'bearer'
    expires_in: int


class LoginUrlResponse(BaseResponse):
    auth_url: str


class LoginJiraSuccessResponse(BaseResponse):
    access_token: str
    refresh_token: str
    token_type: str = 'bearer'
    expires_in: int


class LogoutResponse(BaseResponse):
    status: str
    message: str
