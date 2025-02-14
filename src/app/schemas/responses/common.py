from typing import Generic, List, TypeVar

from src.app.schemas.responses.base import BaseResponse

T = TypeVar('T')


class PaginatedResponse(BaseResponse, Generic[T]):
    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int
