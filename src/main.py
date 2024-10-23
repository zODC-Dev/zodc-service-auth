from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.app.routers.task_router import router as task_router
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

app.include_router(task_router, prefix=settings.API_V1_STR)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
