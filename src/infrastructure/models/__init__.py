from .base import BaseModel, BaseModelWithTimestamps
from .permission import Permission
from .project import Project
from .refresh_token import RefreshToken
from .role import Role
from .role_permission import RolePermission
from .user import User
from .user_performance import UserPerformance
from .user_project_history import UserProjectHistory
from .user_project_role import UserProjectRole

# Update forward references
BaseModel.model_rebuild()
BaseModelWithTimestamps.model_rebuild()
RefreshToken.model_rebuild()
Permission.model_rebuild()
Project.model_rebuild()
Role.model_rebuild()
User.model_rebuild()
UserProjectRole.model_rebuild()
UserProjectHistory.model_rebuild()
UserPerformance.model_rebuild()
RolePermission.model_rebuild()
