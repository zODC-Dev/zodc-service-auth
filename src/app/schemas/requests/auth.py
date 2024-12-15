from pydantic import BaseModel, EmailStr


class LoginEmailPasswordRequest(BaseModel):
    email: EmailStr
    password: str

class LoginSSORequest(BaseModel):
    code_challenge: str

class LoginSSOCallbackRequest(BaseModel):
    code: str
    state: str
    code_verifier: str
