from typing import Optional

from pydantic import Field, field_validator

from .base import BaseRequest


class ProjectCreateRequest(BaseRequest):
    name: str = Field(..., min_length=1, max_length=100)
    key: str = Field(..., min_length=2, max_length=10)
    description: str = Field(..., max_length=200)

    @field_validator('key')
    @classmethod
    def validate_key(cls, v):
        if not v.strip():
            raise ValueError('Key cannot be empty')
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError(
                'Key can only contain alphanumeric characters, underscores, and hyphens')
        return v.upper()  # Store project keys in uppercase


class ProjectUpdateRequest(BaseRequest):
    name: Optional[str] = Field(..., min_length=1, max_length=100)
    key: Optional[str] = Field(..., min_length=2, max_length=10)
    description: Optional[str] = Field(..., max_length=200)

    @field_validator('key')
    @classmethod
    def validate_key(cls, v):
        if not v.strip():
            raise ValueError('Key cannot be empty')
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError(
                'Key can only contain alphanumeric characters, underscores, and hyphens')
        return v.upper()


class LinkJiraProjectRequest(BaseRequest):
    jira_project_id: str
    key: str
    name: str
    description: str
    avatar_url: Optional[str] = None
