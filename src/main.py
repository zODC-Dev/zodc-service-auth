from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from redis.asyncio import Redis

from src.app.middlewares.exception_handler import register_exception_handlers
from src.app.routers.auth_router import router as auth_router
from src.app.routers.internal_router import router as internal_router
from src.app.routers.permission_router import router as permission_router
from src.app.routers.project_router import router as project_router
from src.app.routers.public_auth_router import router as public_auth_router
from src.app.routers.role_router import router as role_router
from src.app.routers.user_router import router as user_router
from src.app.services.nats_subscribe_service import NATSSubscribeService
from src.app.services.project_service import ProjectService
from src.configs.database import get_db, init_db
from src.configs.logger import log
from src.configs.settings import settings
from src.infrastructure.repositories.sqlalchemy_project_repository import SQLAlchemyProjectRepository
from src.infrastructure.repositories.sqlalchemy_role_repository import SQLAlchemyRoleRepository
from src.infrastructure.repositories.sqlalchemy_user_repository import SQLAlchemyUserRepository
from src.infrastructure.services.nats_service import NATSService
from src.infrastructure.services.redis_service import RedisService
from src.infrastructure.services.user_event_service import UserEventService

# Define Prometheus instrumentator first
instrumentator = Instrumentator(
    should_respect_env_var=True,
    env_var_name="ENABLE_METRICS",
    # Add these configurations
    should_instrument_requests_inprogress=True,
    excluded_handlers=[".*admin.*", "/metrics"],
    # env_var_name="ENABLE_METRICS",
    inprogress_name="fastapi_inprogress",
    inprogress_labels=True
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Initialize configurations"""
    # Startup
    log.info(f"Starting up {settings.APP_NAME}")
    await init_db()

    # Initialize Redis
    redis_client = Redis.from_url(
        f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
        encoding="utf-8",
        decode_responses=True
    )
    redis_service = RedisService(redis_client)
    app.state.redis = redis_client

    # Initialize NATS service
    nats_service = NATSService()
    await nats_service.connect()
    app.state.nats = nats_service

    # Initialize repositories
    db_generator = get_db()
    db = await anext(db_generator)  # Get the actual session from the generator

    user_event_service = UserEventService(nats_service)

    user_repository = SQLAlchemyUserRepository(db, user_event_service, redis_service)
    project_repository = SQLAlchemyProjectRepository(db)
    role_repository = SQLAlchemyRoleRepository(db)

    project_service = ProjectService(
        project_repository,
        role_repository,
        user_repository,
        nats_service
    )

    # Start subscribers
    nats_subscribe_service = NATSSubscribeService(
        nats_service,
        project_service
    )

    await nats_subscribe_service.start_nats_subscribers()

    yield

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

# Add Prometheus instrumentation AFTER FastAPI app creation
instrumentator.instrument(app).expose(app, include_in_schema=True)

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
    prefix=settings.API_V1_STR + "/private",
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
app.include_router(
    internal_router,
    prefix=settings.API_V1_STR + "/internal",
    tags=["internal"]
)

# Register exception handlers
register_exception_handlers(app)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("src.main:app", host="0.0.0.0",
                port=settings.PORT, reload=True)
