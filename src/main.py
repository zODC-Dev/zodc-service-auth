from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.app.routers.auth_router import router as auth_router
from src.app.routers.internal_router import router as internal_router
from src.app.routers.permission_router import router as permission_router
from src.app.routers.project_router import router as project_router
from src.app.routers.public_auth_router import router as public_auth_router
from src.app.routers.role_router import router as role_router
from src.app.routers.user_router import router as user_router
from src.configs.database import init_db
from src.configs.logger import log
from src.configs.settings import settings
from src.infrastructure.services.nats_service import NATSService


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Initialize configurations"""
    # Startup
    log.info(f"Starting up {settings.APP_NAME}")
    await init_db()

    # Initialize NATS service
    nats_service = NATSService()
    await nats_service.connect()
    app.state.nats = nats_service

    yield  # This is where the FastAPI app runs

    # Shutdown
    log.info(f"Shutting down {settings.APP_NAME}")
    if hasattr(app.state, "nats"):
        await app.state.nats.disconnect()


app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
    lifespan=lifespan,
    docs_url="/docs",
    openapi_url="/openapi.json",
)

if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin)
                       for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Public routes (no auth required)
app.include_router(
    public_auth_router,
    prefix=settings.API_V1_STR + "/public",
    tags=["authentication"]
)

# Protected routes (auth required)
app.include_router(
    auth_router,
    prefix=settings.API_V1_STR + "/auth",
    tags=["authentication"]
)

app.include_router(user_router, prefix=settings.API_V1_STR +
                   "/users", tags=["users"])
app.include_router(role_router, prefix=settings.API_V1_STR +
                   "/roles", tags=["roles"])
app.include_router(permission_router, prefix=settings.API_V1_STR +
                   "/permissions", tags=["permissions"])
app.include_router(project_router, prefix=settings.API_V1_STR +
                   "/projects", tags=["projects"])
app.include_router(internal_router, prefix=settings.API_V1_STR +
                   "/internal", tags=["internal"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("src.main:app", host="0.0.0.0",
                port=settings.PORT, reload=True)
