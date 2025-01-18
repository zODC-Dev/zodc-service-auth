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

    # Redis settings
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str | None = None  # Add password if Redis is secured
    REDIS_DB: int = 0  # Default Redis database

    # FastAPI Azure Auth settings
    BACKEND_CORS_ORIGINS: list[str | AnyHttpUrl] = [
        "http://localhost:8000", "http://localhost:4200"]
    OPENAPI_CLIENT_ID: str = ""
    APP_CLIENT_ID: str = ""

    # Client and server settings
    CLIENT_AZURE_CLIENT_ID: str = ""
    CLIENT_AZURE_TENANT_ID: str = ""
    CLIENT_AZURE_REDIRECT_URI: str = ""
    CLIENT_AZURE_CLIENT_SECRET: str = ""

    # NATS settings
    NATS_URL: str = "nats://localhost:4222"
    NATS_CLIENT_NAME: str = "auth_service"
    NATS_CLUSTER_ID: str = "test-cluster"
    NATS_USERNAME: str = "myuser"
    NATS_PASSWORD: str = "mypassword"

    # Refresh token settings
    REFRESH_TOKEN_EXPIRATION_TIME: int = 60 * 60 * 24 * 30  # 30 days
    MICROSOFT_TOKEN_EXPIRATION_TIME: int = 60 * 60 * 24 * 1  # 1 day
    JIRA_TOKEN_EXPIRATION_TIME: int = 60 * 60 * 24 * 1  # 1 day

    # Jira OAuth settings
    JIRA_CLIENT_ID: str
    JIRA_CLIENT_SECRET: str
    JIRA_REDIRECT_URI: str

    class Config:
        """Configuration settings."""

        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()
