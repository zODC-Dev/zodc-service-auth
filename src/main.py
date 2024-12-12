from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Security
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel

from src.app.routers.auth_router import router as auth_router
from src.app.routers.calendar_router import router as calendar_router
from src.app.routers.task_router import router as task_router
from src.configs.auth import azure_scheme
from src.configs.database import engine
from src.configs.logger import log
from src.configs.settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Initialize configurations"""
    # Startup
    log.info(f"Starting up {settings.APP_NAME}")
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    log.info("Database tables created")

    """
    Load OpenID config on startup.
    """
    await azure_scheme.openid_config.load_config()

    yield  # This is where the FastAPI app runs

    # Shutdown
    log.info(f"Shutting down {settings.APP_NAME}")
    await engine.dispose()


app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
    lifespan=lifespan,
    swagger_ui_init_oauth={
        "usePkceWithAuthorizationCodeGrant": True,
        "clientId": settings.CLIENT_AZURE_CLIENT_ID,
        "appName": settings.APP_NAME,
    },
)

if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.get("/", dependencies=[Security(azure_scheme)])
async def root():
    """Endpoint for testing security"""
    return {"message": "Hello World"}


app.include_router(task_router, prefix=settings.API_V1_STR + "/tasks", tags=["tasks"])
app.include_router(auth_router, prefix=settings.API_V1_STR + "/auth", tags=["authentication"])
app.include_router(calendar_router, prefix=settings.API_V1_STR + "/calendars", tags=["calendars"])

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("src.main:app", host="0.0.0.0", port=settings.PORT, reload=True)
