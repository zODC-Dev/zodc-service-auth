from typing import Optional

from pydantic import BaseModel, Field


class AssignRoleRequest(BaseModel):
    """Request model for assigning a role to a user"""
    user_id: int = Field(..., description="ID of the user to assign the role to")
    role_name: str = Field(..., description="Name of the role to assign")


class AssignRoleResponse(BaseModel):
    """Response model for role assignment request"""
    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="Success or error message")
    user_id: int = Field(..., description="ID of the user that was processed")
    role_name: str = Field(..., description="Name of the role that was assigned")
    error_code: Optional[str] = Field(None, description="Error code if an error occurred")


class AssignProjectRoleRequest(BaseModel):
    """Request model for assigning a role to a user in a project"""
    user_id: int = Field(..., description="ID of the user to assign the role to")
    role_name: str = Field(..., description="Name of the role to assign")
    project_key: str = Field(..., description="Key of the project to assign the role in")


class AssignProjectRoleResponse(BaseModel):
    """Response model for project role assignment request"""
    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="Success or error message")
    user_id: int = Field(..., description="ID of the user that was processed")
    role_name: str = Field(..., description="Name of the role that was assigned")
    project_key: str = Field(..., description="Key of the project where the role was assigned")
    error_code: Optional[str] = Field(None, description="Error code if an error occurred")


class UnassignProjectRoleRequest(BaseModel):
    """Request model for unassigning a role from a user in a project"""
    user_id: int = Field(..., description="ID of the user to unassign the role from")
    role_name: str = Field(..., description="Name of the role to unassign")
    project_key: str = Field(..., description="Key of the project to unassign the role from")


class UnassignProjectRoleResponse(BaseModel):
    """Response model for project role unassignment request"""
    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="Success or error message")
    user_id: int = Field(..., description="ID of the user that was processed")
    role_name: str = Field(..., description="Name of the role that was unassigned")
    project_key: str = Field(..., description="Key of the project where the role was unassigned")
    error_code: Optional[str] = Field(None, description="Error code if an error occurred")
