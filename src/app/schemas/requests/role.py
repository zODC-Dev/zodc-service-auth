from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class RoleCreateRequest(BaseModel):
    name: str = Field(..., min_length=3, max_length=50)
    description: Optional[str] = Field(None, max_length=200)
    permission_names: List[str] = Field(default_factory=list)
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


class RoleUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=50)
    description: Optional[str] = Field(None, max_length=200)
    permission_names: Optional[List[str]] = None
    is_active: Optional[bool] = None
    is_system_role: Optional[bool] = None

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


class AssignSystemRoleRequest(BaseModel):
    user_id: int = Field(..., description="ID of the user")
    role_name: str = Field(...,
                           description="Name of the system role to assign")


class AssignProjectRoleRequest(BaseModel):
    user_id: int = Field(..., description="ID of the user")
    role_name: str = Field(...,
                           description="Name of the project role to assign")
