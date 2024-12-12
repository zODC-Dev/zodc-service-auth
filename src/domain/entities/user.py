from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class User(BaseModel):
    id: int
    email: str
    full_name: Optional[str]
    roles: List[str]
    permissions: List[str]
    is_active: bool
    created_at: datetime
    microsoft_id: Optional[str] = None
