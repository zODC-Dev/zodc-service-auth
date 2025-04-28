from typing import List, Optional

from fastapi import HTTPException

from src.app.schemas.requests.user import (
    CreateUserPerformanceRequest,
    UpdateUserPerformanceRequest,
    UpdateUserProfileRequest,
)
from src.app.schemas.responses.base import StandardResponse
from src.app.schemas.responses.performance import PerformanceResponse, ProjectPerformanceResponse
from src.app.schemas.responses.project import ProjectAssigneeResponse
from src.app.schemas.responses.user import AdminUserResponse, UserWithProfileResponse
from src.app.services.user_service import UserService
from src.domain.entities.user import UserProfileUpdate
from src.domain.entities.user_performance import UserPerformanceCreate, UserPerformanceUpdate
from src.domain.exceptions.user_exceptions import UserNotFoundError


class UserController:
    def __init__(self, user_service: UserService):
        self.user_service = user_service

    async def get_me(self, user_id: int) -> StandardResponse[UserWithProfileResponse]:
        try:
            user = await self.user_service.get_current_user(user_id)
            return StandardResponse(
                message="User profile retrieved successfully",
                data=UserWithProfileResponse.from_domain(user)
            )
        except UserNotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e)) from e
        except Exception as e:
            raise HTTPException(
                status_code=500, detail="Failed to get user information") from e

    async def get_users(
        self,
        search: Optional[str] = None
    ) -> StandardResponse[List[ProjectAssigneeResponse]]:
        """Get all users with their roles.

        Args:
            search: Optional search term to filter users by name or email

        Returns:
            List of users with their roles
        """
        try:
            users = await self.user_service.get_users(
                search=search
            )

            return StandardResponse(
                message="Users retrieved successfully",
                data=[
                    ProjectAssigneeResponse.from_user(user)
                    for user in users
                ]
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to retrieve users: {str(e)}"
            ) from e

    async def get_users_for_admin(
        self,
        search: Optional[str] = None
    ) -> StandardResponse[List[AdminUserResponse]]:
        """Get all users with their roles.

        Args:
            search: Optional search term to filter users by name or email

        Returns:
            List of users with their roles
        """
        try:
            users = await self.user_service.get_users(
                search=search
            )

            return StandardResponse(
                message="Users retrieved successfully",
                data=[
                    AdminUserResponse.from_user(user)
                    for user in users
                ]
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to retrieve users: {str(e)}"
            ) from e

    async def get_user_profile(
        self,
        user_id: int,
    ) -> StandardResponse[UserWithProfileResponse]:
        """Get a user's complete profile

        Args:
            user_id: ID of the user to get profile for

        Returns:
            User profile information
        """
        try:
            user = await self.user_service.get_user_with_profile_data(user_id)

            profile_response = UserWithProfileResponse.from_domain(user)

            return StandardResponse(
                message="User profile retrieved successfully",
                data=profile_response
            )
        except UserNotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e)) from e
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to retrieve user profile: {str(e)}"
            ) from e

    async def get_user_performance(
        self,
        user_id: int,
        quarter: Optional[int] = None,
        year: Optional[int] = None
    ) -> StandardResponse[List[PerformanceResponse]]:
        """Get a user's performance records

        Args:
            user_id: ID of the user to get performance for
            quarter: Optional quarter to filter by (1-4)
            year: Optional year to filter by

        Returns:
            List of performance records
        """
        try:
            performance_records = await self.user_service.get_user_performance(
                user_id,
                quarter=quarter,
                year=year
            )

            return StandardResponse(
                message="User performance records retrieved successfully",
                data=[
                    PerformanceResponse.from_domain(record)
                    for record in performance_records
                ]
            )
        except UserNotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e)) from e
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to retrieve user performance: {str(e)}"
            ) from e

    async def get_user_performance_by_project(
        self,
        user_id: int,
        quarter: Optional[int] = None,
        year: Optional[int] = None
    ) -> StandardResponse[List[ProjectPerformanceResponse]]:
        """Get a user's performance records grouped by project

        Args:
            user_id: ID of the user to get performance for
            quarter: Optional quarter to filter by (1-4)
            year: Optional year to filter by

        Returns:
            List of project performance records
        """
        try:
            # Get performance records grouped by project
            project_performances = await self.user_service.get_user_performance_by_project(
                user_id,
                quarter=quarter,
                year=year
            )

            # Convert to response format
            response_data = []
            for project_id, project_data in project_performances.items():
                project_name = project_data["name"]
                project_key = project_data["key"]
                performances = project_data["performances"]

                response_data.append(
                    ProjectPerformanceResponse.from_performances(
                        project_id=project_id,
                        project_name=project_name,
                        project_key=project_key,
                        performances=performances
                    )
                )

            return StandardResponse(
                message="User performance records retrieved successfully",
                data=response_data
            )
        except UserNotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e)) from e
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to retrieve user performance: {str(e)}"
            ) from e

    async def update_my_profile(
        self,
        user_id: int,
        request: UpdateUserProfileRequest
    ) -> StandardResponse[UserWithProfileResponse]:
        try:
            profile_data = UserProfileUpdate(
                job_title=request.job_title,
                location=request.location,
                phone_number=request.phone_number,
                joined_date=request.joined_date,
                profile_data={
                    "primary_skills": request.primary_skills,
                    "secondary_skills": request.secondary_skills,
                    "education": request.education,
                    "certifications": request.certifications,
                    "professional_summary": request.professional_summary
                }
            )
            user = await self.user_service.update_user_profile(user_id, profile_data)
            return StandardResponse(
                message="User profile updated successfully",
                data=UserWithProfileResponse.from_domain(user)
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to update user profile: {str(e)}"
            ) from e

    async def create_user_performance(
        self,
        user_id: int,
        request: CreateUserPerformanceRequest
    ) -> StandardResponse[PerformanceResponse]:
        """Create a performance record for a user

        Args:
            user_id: ID of the user to create performance for
            request: Performance data

        Returns:
            Created performance record
        """
        try:
            # Create performance record
            performance_data = UserPerformanceCreate(
                user_id=user_id,
                project_id=request.project_id,
                quarter=request.quarter,
                year=request.year,
                overall=request.overall,
                code_quality=request.code_quality,
                test_coverage=request.test_coverage,
                documentation=request.documentation,
                feedback=request.feedback,
                strengths=request.strengths,
                areas_for_improvement=request.areas_for_improvement
            )

            performance = await self.user_service.create_user_performance(performance_data)

            return StandardResponse(
                message="Performance record created successfully",
                data=PerformanceResponse.from_domain(performance)
            )
        except UserNotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e)) from e
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to create performance record: {str(e)}"
            ) from e

    async def update_user_performance(
        self,
        performance_id: int,
        request: UpdateUserPerformanceRequest
    ) -> StandardResponse[PerformanceResponse]:
        """Update a performance record

        Args:
            performance_id: ID of the performance record to update
            request: Updated performance data

        Returns:
            Updated performance record
        """
        try:
            # Prepare update data
            performance_data = UserPerformanceUpdate(
                quarter=request.quarter,
                year=request.year,
                overall=request.overall,
                code_quality=request.code_quality,
                test_coverage=request.test_coverage,
                documentation=request.documentation,
                feedback=request.feedback,
                strengths=request.strengths,
                areas_for_improvement=request.areas_for_improvement
            )

            # Update performance
            performance = await self.user_service.update_user_performance(performance_id, performance_data)

            if not performance:
                raise HTTPException(status_code=404, detail=f"Performance record with id {performance_id} not found")

            return StandardResponse(
                message="Performance record updated successfully",
                data=PerformanceResponse.from_domain(performance)
            )
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to update performance record: {str(e)}"
            ) from e
