from pydantic_settings import BaseSettings
from pydantic import PostgresDsn

class Settings(BaseSettings):
    # Database settings
    DATABASE_URL: PostgresDsn

    # Application settings
    APP_NAME: str = "zODC Backend"
    DEBUG: bool = False

    # API settings
    API_V1_STR: str = "/api/v1"

    # JWT settings
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Logging
    LOG_LEVEL: str = "INFO"

    # Port
    PORT: int = 8000

    # Azure AD settings
    AZURE_AD_TENANT_ID: str
    AZURE_AD_CLIENT_ID: str
    AZURE_AD_CLIENT_SECRET: str
    AZURE_AD_REDIRECT_URI: str
    AZURE_AD_OBJECT_ID: str
    AZURE_AD_CLIENT_SECRET_ID: str
    AZURE_AD_SCOPES: list = ["User.Read", "Calendars.Read", "Calendars.ReadWrite", "offline_access", "openid", "profile", "email"]

    # Redis settings
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = None  # Add password if Redis is secured
    REDIS_DB: int = 0  # Default Redis database

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

settings = Settings()