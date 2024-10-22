from fastapi import FastAPI
from src.app.routers import task_router
from src.configs.database import engine, Base
from src.configs.logger import log
from src.scripts.run_migrations import run_migrations
from src.configs.settings import settings
import asyncio

Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG)

app.include_router(task_router, prefix=settings.API_V1_STR)

if __name__ == "__main__":
    import uvicorn
    log.info("Starting the server")
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=settings.DEBUG)
