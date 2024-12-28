from .permission import Permission
from .project import Project
from .role import Role
from .user import User
from .user_project_role import UserProjectRole

Permission.model_rebuild()
Project.model_rebuild()
Role.model_rebuild()
User.model_rebuild()
UserProjectRole.model_rebuild()
