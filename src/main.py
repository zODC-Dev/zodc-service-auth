from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.app.routers.task_router import router as task_router
from src.app.routers.auth_router import router as auth_router
from src.app.routers.event_router import router as event_router
from src.app.routers.calendar_router import router as calendar_router
from src.configs.database import engine, Base
from src.configs.logger import log
from src.configs.settings import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    log.info(f"Starting up {settings.APP_NAME}")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    log.info("Database tables created")
    
    yield  # This is where the FastAPI app runs
    
    # Shutdown
    log.info(f"Shutting down {settings.APP_NAME}")
    await engine.dispose()

app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG, lifespan=lifespan)

app.include_router(task_router, prefix=settings.API_V1_STR + "/tasks", tags=["tasks"])
app.include_router(auth_router, prefix=settings.API_V1_STR  + "/auth", tags=["authentication"])
app.include_router(event_router, prefix=settings.API_V1_STR + "/events", tags=['events'])
app.include_router(calendar_router, prefix=settings.API_V1_STR + "/calendars", tags=['calendars'])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=settings.PORT, reload=True)
