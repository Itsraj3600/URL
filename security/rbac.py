"""
Role-Based Access Control (RBAC) system for CINE3600.

Implements a hierarchical role system with fine-grained permissions.
"""

from enum import Enum
from typing import Set, Optional


class Role(Enum):
    """Role hierarchy from highest to lowest privilege."""
    OWNER = "owner"
    ADMIN = "admin"
    MODERATOR = "moderator"
    VIEWER = "viewer"
    API = "api"


class Permission(Enum):
    """Granular permissions across the system."""
    # User management
    MANAGE_USERS = "manage_users"
    MANAGE_ROLES = "manage_roles"
    VIEW_USERS = "view_users"
    
    # Dashboard access
    VIEW_DASHBOARD = "view_dashboard"
    VIEW_WORKERS = "view_workers"
    CONTROL_WORKERS = "control_workers"
    VIEW_LOGS = "view_logs"
    
    # Content management
    MANAGE_CHANNELS = "manage_channels"
    MANAGE_INDEXING = "manage_indexing"
    VIEW_INDEXING = "view_indexing"
    
    # AI system
    MANAGE_AI = "manage_ai"
    USE_AI = "use_ai"
    VIEW_AI_ANALYTICS = "view_ai_analytics"
    
    # Security
    MANAGE_SECURITY = "manage_security"
    VIEW_AUDIT_LOGS = "view_audit_logs"
    MANAGE_API_KEYS = "manage_api_keys"
    
    # System
    MANAGE_SETTINGS = "manage_settings"
    BACKUP_RESTORE = "backup_restore"
    VIEW_HEALTH = "view_health"


# Permission matrix: role -> set of permissions
ROLE_PERMISSIONS: dict[Role, Set[Permission]] = {
    Role.OWNER: {
        Permission.MANAGE_USERS,
        Permission.MANAGE_ROLES,
        Permission.VIEW_USERS,
        Permission.VIEW_DASHBOARD,
        Permission.VIEW_WORKERS,
        Permission.CONTROL_WORKERS,
        Permission.VIEW_LOGS,
        Permission.MANAGE_CHANNELS,
        Permission.MANAGE_INDEXING,
        Permission.VIEW_INDEXING,
        Permission.MANAGE_AI,
        Permission.USE_AI,
        Permission.VIEW_AI_ANALYTICS,
        Permission.MANAGE_SECURITY,
        Permission.VIEW_AUDIT_LOGS,
        Permission.MANAGE_API_KEYS,
        Permission.MANAGE_SETTINGS,
        Permission.BACKUP_RESTORE,
        Permission.VIEW_HEALTH,
    },
    Role.ADMIN: {
        Permission.VIEW_USERS,
        Permission.VIEW_DASHBOARD,
        Permission.VIEW_WORKERS,
        Permission.CONTROL_WORKERS,
        Permission.VIEW_LOGS,
        Permission.MANAGE_CHANNELS,
        Permission.MANAGE_INDEXING,
        Permission.VIEW_INDEXING,
        Permission.MANAGE_AI,
        Permission.USE_AI,
        Permission.VIEW_AI_ANALYTICS,
        Permission.VIEW_AUDIT_LOGS,
        Permission.MANAGE_API_KEYS,
        Permission.MANAGE_SETTINGS,
        Permission.VIEW_HEALTH,
    },
    Role.MODERATOR: {
        Permission.VIEW_USERS,
        Permission.VIEW_DASHBOARD,
        Permission.VIEW_WORKERS,
        Permission.VIEW_LOGS,
        Permission.MANAGE_CHANNELS,
        Permission.VIEW_INDEXING,
        Permission.USE_AI,
        Permission.VIEW_AI_ANALYTICS,
        Permission.VIEW_AUDIT_LOGS,
        Permission.VIEW_HEALTH,
    },
    Role.VIEWER: {
        Permission.VIEW_DASHBOARD,
        Permission.VIEW_WORKERS,
        Permission.VIEW_LOGS,
        Permission.VIEW_INDEXING,
        Permission.USE_AI,
        Permission.VIEW_AI_ANALYTICS,
        Permission.VIEW_HEALTH,
    },
    Role.API: {
        Permission.USE_AI,
        Permission.VIEW_HEALTH,
    },
}


def has_permission(role: Role, permission: Permission) -> bool:
    """Check if a role has a specific permission."""
    return permission in ROLE_PERMISSIONS.get(role, set())


def has_any_permission(role: Role, permissions: Set[Permission]) -> bool:
    """Check if a role has any of the given permissions."""
    user_perms = ROLE_PERMISSIONS.get(role, set())
    return bool(user_perms & permissions)


def has_all_permissions(role: Role, permissions: Set[Permission]) -> bool:
    """Check if a role has all of the given permissions."""
    user_perms = ROLE_PERMISSIONS.get(role, set())
    return permissions.issubset(user_perms)


def get_role_hierarchy_level(role: Role) -> int:
    """Get the hierarchy level of a role (lower = higher privilege)."""
    hierarchy = {
        Role.OWNER: 0,
        Role.ADMIN: 1,
        Role.MODERATOR: 2,
        Role.VIEWER: 3,
        Role.API: 4,
    }
    return hierarchy.get(role, 999)


def can_manage_role(manager_role: Role, target_role: Role) -> bool:
    """Check if manager_role can manage target_role."""
    return get_role_hierarchy_level(manager_role) < get_role_hierarchy_level(target_role)
