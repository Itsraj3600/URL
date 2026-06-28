"""
Sprint 8: Enterprise Security & Administration

Provides complete security infrastructure for multi-user CINE3600 deployment.
"""

import logging
from motor.motor_asyncio import AsyncIOMotorDatabase

from .rbac import Role, Permission, has_permission, can_manage_role
from .jwt_auth import JWTAuth
from .user_db import UserDB
from .api_keys import APIKeyManager
from .secrets import SecretsManager
from .audit import AuditLogger, AuditAction
from .alerts import SecurityAlerts

logger = logging.getLogger(__name__)


class SecurityManager:
    """Central security manager coordinating all security modules."""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.jwt = JWTAuth(db)
        self.users = UserDB(db)
        self.api_keys = APIKeyManager(db)
        self.secrets = SecretsManager(db)
        self.audit = AuditLogger(db)
        self.alerts = SecurityAlerts(db)

    async def initialize(self):
        """Initialize all security modules."""
        try:
            logger.info("Initializing security modules...")
            await self.jwt.create_indexes()
            await self.users.create_indexes()
            await self.api_keys.create_indexes()
            await self.secrets.create_indexes()
            await self.audit.create_indexes()
            await self.alerts.create_indexes()
            logger.info("Security modules initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing security: {e}")
            raise

    async def create_default_users(self):
        """Create default admin user."""
        try:
            existing = await self.users.get_user_by_username("admin")
            if existing:
                logger.info("Default admin user already exists")
                return

            user_id = await self.users.create_user(
                username="admin",
                email="admin@cine3600.local",
                password="admin123",  # MUST be changed in production
                role=Role.OWNER,
                full_name="Administrator",
            )

            if user_id:
                logger.info("Created default admin user")
                await self.audit.log(
                    AuditAction.USER_CREATED,
                    "system",
                    "info",
                    details={"user_id": user_id, "username": "admin"},
                )
        except Exception as e:
            logger.error(f"Error creating default users: {e}")


__all__ = [
    "Role",
    "Permission",
    "AuditAction",
    "SecurityManager",
    "has_permission",
    "can_manage_role",
]
