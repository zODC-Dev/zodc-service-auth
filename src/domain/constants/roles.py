from enum import Enum


class SystemRoles(str, Enum):
    ADMIN = "admin"
    USER = "user"  # ODC Members
    PRODUCT_OWNER = "product_owner"
    ODC_MANAGER = "odc_manager"


class ProjectRoles(str, Enum):
    PROJECT_PRODUCT_OWNER = "project_product_owner"
    FEATURE_LEADER = "feature_leader"
    TEAM_MEMBER = "team_member"
