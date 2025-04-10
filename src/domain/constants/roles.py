from enum import Enum


class SystemRoles(str, Enum):
    ADMIN = "admin"
    USER = "member"  # ODC Members
    PRODUCT_OWNER = "product_owner"
    ODC_MANAGER = "odc_manager"
    HUMAN_RESOURCE = "human_resource"
    GUEST = "guest"


class ProjectRoles(str, Enum):
    PROJECT_PRODUCT_OWNER = "project_product_owner"
    FEATURE_LEADER = "project_feature_leader"
    TEAM_MEMBER = "project_member"
