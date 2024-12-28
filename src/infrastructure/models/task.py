from typing import Optional

from sqlmodel import Field

from .base import BaseModelWithTimestamps


class Task(BaseModelWithTimestamps, table=True):
    __tablename__ = 'tasks'

    id: Optional[int] = Field(default=None, primary_key=True,
                              index=True, sa_column_kwargs={"autoincrement": True})
    title: str = Field(index=True)
    description: str
    is_completed: bool = Field(default=False)
