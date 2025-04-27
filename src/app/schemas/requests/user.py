from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class UserIdsRequest(BaseModel):
    user_ids: List[int] = Field(..., description="List of user IDs to retrieve", alias="userIds")


class UpdateUserProfileRequest(BaseModel):
    job_title: Optional[str] = Field(None, description="Job title", alias="jobTitle")
    location: Optional[str] = Field(None, description="Location", alias="location")
    phone_number: Optional[str] = Field(None, description="Phone number", alias="phoneNumber")
    joined_date: Optional[str] = Field(None, description="Joined date", alias="joinedDate")
    primary_skills: Optional[List[Dict[str, Any]]] = Field(None, description="List of primary skills")
    secondary_skills: Optional[List[Dict[str, Any]]] = Field(None, description="List of secondary skills")
    education: Optional[str] = Field(None, description="Education")
    certifications: Optional[str] = Field(None, description="Certifications")


class CreateUserPerformanceRequest(BaseModel):
    project_id: int = Field(..., description="Project ID", alias="projectId")
    quarter: int = Field(..., description="Quarter (1-4)", ge=1, le=4)
    year: int = Field(..., description="Year")
    overall: float = Field(..., description="Overall performance score", ge=0, le=5)
    code_quality: Optional[float] = Field(None, description="Code quality score", ge=0, le=5, alias="codeQuality")
    test_coverage: Optional[float] = Field(None, description="Test coverage score", ge=0, le=5, alias="testCoverage")
    documentation: Optional[float] = Field(None, description="Documentation score", ge=0, le=5)
    feedback: Optional[str] = Field(None, description="General feedback")
    strengths: Optional[str] = Field(None, description="Strengths")
    areas_for_improvement: Optional[str] = Field(
        None, description="Areas for improvement", alias="areasForImprovement")


class UpdateUserPerformanceRequest(BaseModel):
    quarter: Optional[int] = Field(None, description="Quarter (1-4)", ge=1, le=4)
    year: Optional[int] = Field(None, description="Year")
    overall: Optional[float] = Field(None, description="Overall performance score", ge=0, le=5)
    code_quality: Optional[float] = Field(None, description="Code quality score", ge=0, le=5, alias="codeQuality")
    test_coverage: Optional[float] = Field(None, description="Test coverage score", ge=0, le=5, alias="testCoverage")
    documentation: Optional[float] = Field(None, description="Documentation score", ge=0, le=5)
    feedback: Optional[str] = Field(None, description="General feedback")
    strengths: Optional[str] = Field(None, description="Strengths")
    areas_for_improvement: Optional[str] = Field(
        None, description="Areas for improvement", alias="areasForImprovement")
