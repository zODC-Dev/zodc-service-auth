from typing import List

from pydantic import BaseModel, Field


class UserIdsRequest(BaseModel):
    user_ids: List[int] = Field(..., description="List of user IDs to retrieve", alias="userIds")
