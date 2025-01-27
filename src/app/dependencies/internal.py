from fastapi import Depends

from src.app.controllers.internal_controller import InternalController

from .common import get_token_service


async def get_internal_controller(
    token_service=Depends(get_token_service)
) -> InternalController:
    """Get internal controller"""
    return InternalController(token_service)
