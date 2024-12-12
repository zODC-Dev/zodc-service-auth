from datetime import datetime
from typing import List, Optional

from pydantic import EmailStr
from sqlmodel import JSON, Field, SQLModel


class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True)
    full_name: str = Field(max_length=255)
    is_active: bool = Field(default=True)
    roles: List[str] = Field(default=["user"], sa_type=JSON)
    permissions: List[str] = Field(default_factory=list, sa_type=JSON)

class User(UserBase, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    password: Optional[str] = Field(default=None, max_length=60)
    microsoft_id: Optional[str] = Field(default=None, unique=True)
    microsoft_token: Optional[str] = Field(default=None)
    microsoft_refresh_token: Optional[str] = Field(default=None, max_length=255)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(),
        sa_column_kwargs={"server_default": "NOW()", "nullable": False}
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column_kwargs={"onupdate": "NOW()"}
    )

class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=60)

class UserCreateSSO(UserBase):
    microsoft_id: str

class UserRead(UserBase):
    id: int
    created_at: datetime
    microsoft_id: Optional[str] = None

class UserUpdate(SQLModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None
