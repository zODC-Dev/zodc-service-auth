from typing import List, Optional

from pydantic import Field, field_validator

from .base import BaseRequest


class RoleCreateRequest(BaseRequest):
    name: str = Field(..., min_length=3, max_length=50)
    description: Optional[str] = Field(None, max_length=200)
    permissions: List[int] = Field(default_factory=list)  # permission ids
    is_system_role: bool = Field(default=False)

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError('Name cannot be empty')
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError(
                'Name can only contain alphanumeric characters, underscores, and hyphens')
        return v.lower()  # Store role names in lowercase


class RoleUpdateRequest(BaseRequest):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    is_system_role: Optional[bool] = None
    permissions: Optional[List[int]] = None  # Thay thế permission_names bằng permissions

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if v is None:
            return v
        if not v.strip():
            raise ValueError('Name cannot be empty')
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError(
                'Name can only contain alphanumeric characters, underscores, and hyphens')
        return v.lower()


class AssignSystemRoleRequest(BaseRequest):
    user_id: int = Field(..., description="ID of the user")
    role_name: str = Field(...,
                           description="Name of the system role to assign")


class AssignProjectRoleRequest(BaseRequest):
    user_id: int = Field(..., description="ID of the user")
    role_name: str = Field(...,
                           description="Name of the project role to assign")
