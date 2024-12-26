from .base import BaseModel, BaseModelWithTimestamps
from .project import Project
from .role import Role
from .user import User
from .user_project_role import UserProjectRole

# Update forward references
BaseModel.model_rebuild()
BaseModelWithTimestamps.model_rebuild()
User.model_rebuild()
Project.model_rebuild()
Role.model_rebuild()
UserProjectRole.model_rebuild()
