# src/infrastructure/models/__init__.py
from src.configs.logger import logger

from .project import Project
from .role import Role
from .user import User
from .user_project_role import UserProjectRole

logger.info("Loading models...")

# Update forward references
User.model_rebuild()
Project.model_rebuild()
Role.model_rebuild()
UserProjectRole.model_rebuild()
