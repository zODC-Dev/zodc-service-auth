from fastapi.security import OAuth2PasswordBearer

# Centralize OAuth2 configuration
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="api/v1/auth/token",
    scheme_name="JWT",
    description="JWT authentication"
)
