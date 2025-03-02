from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from src.domain.constants.auth import TokenType


class TokenEvent(BaseModel):
    user_id: int
    access_token: str
    refresh_token: Optional[str]
    expires_at: datetime
    token_type: TokenType
    created_at: datetime
    expires_in: int
