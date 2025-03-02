from typing import Optional, TypeVar

from src.app.schemas.responses.base import StandardResponse

T = TypeVar('T')


def wrap_response(data: Optional[T] = None, message: str = "Success") -> StandardResponse[T]:
    """Wrap any response data in the standard response format.

    Args:
        data: The response data to wrap
        message: A message describing the response

    Returns:
        A StandardResponse object containing the data and message
    """
    return StandardResponse(message=message, data=data)
