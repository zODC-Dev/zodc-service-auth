from pydantic import AnyHttpUrl, PostgresDsn
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings.

    Args:
        BaseSettings: Base settings class
    """

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
    AZURE_AD_SCOPES: list[str] = [
        "openid",
        "profile",
        "email",
        "offline_access",
        "https://graph.microsoft.com/user.read",
        "https://graph.microsoft.com/calendars.read",
        "https://graph.microsoft.com/calendars.readwrite",
    ]

    # Redis settings
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str | None = None  # Add password if Redis is secured
    REDIS_DB: int = 0  # Default Redis database

    # FastAPI Azure Auth settings
    BACKEND_CORS_ORIGINS: list[str | AnyHttpUrl] = ["http://localhost:8000", "http://localhost:4200"]
    OPENAPI_CLIENT_ID: str = ""
    APP_CLIENT_ID: str = ""

    # Client and server settings
    CLIENT_AZURE_CLIENT_ID: str = ""
    CLIENT_AZURE_TENANT_ID: str = ""
    CLIENT_AZURE_REDIRECT_URI: str = ""
    CLIENT_AZURE_CLIENT_SECRET: str = ""

    SERVER_AZURE_CLIENT_ID: str = ""
    SERVER_AZURE_TENANT_ID: str = ""
    SERVER_AZURE_REDIRECT_URI: str = ""
    SERVER_AZURE_CLIENT_SECRET: str = ""

    class Config:
        """Configuration settings."""

        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()
