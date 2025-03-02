from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.app.schemas.responses.base import StandardResponse


def register_exception_handlers(app: FastAPI):
    """Register exception handlers for the FastAPI app."""
    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content=StandardResponse(
                message=str(exc) or "Internal server error",
                data=None
            ).model_dump()
        )

    # Add more specific exception handlers as needed
