from typing import Optional

from pydantic import BaseModel, Field, field_validator


class ProjectCreateRequest(BaseModel):
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


class ProjectUpdateRequest(BaseModel):
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


class LinkJiraProjectRequest(BaseModel):
    jira_project_id: str
    key: str
    name: str
    description: Optional[str] = None
