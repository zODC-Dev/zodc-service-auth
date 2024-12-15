from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class Task(SQLModel, table=True):
    __tablename__ = 'tasks'

    id: Optional[int] = Field(default=None, primary_key=True, index=True, sa_column_kwargs={"autoincrement": True})
    title: str = Field(index=True)
    description: str
    is_completed: bool = Field(default=False)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(), sa_column_kwargs={"server_default": "NOW()", "nullable": False}
    )
    updated_at: datetime | None = Field(default=None, sa_column_kwargs={"onupdate": "NOW()"})
