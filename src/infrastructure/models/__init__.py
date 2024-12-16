# src/infrastructure/models/__init__.py
from .project import Project
from .role import Role
from .user import User
from .user_project_role import UserProjectRole

# Update forward references
User.model_rebuild()
Project.model_rebuild()
Role.model_rebuild()
UserProjectRole.model_rebuild()
