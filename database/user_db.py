"""
User database models for CINE3600.

Manages user accounts, roles, and permissions.
"""

import logging
from datetime import datetime
from typing import Optional, List
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from bson import ObjectId
import bcrypt

from security.rbac import Role, Permission

logger = logging.getLogger(__name__)


class UserDB:
    """Database operations for user management."""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.users = db.users
        self.user_sessions = db.user_sessions

    async def create_indexes(self):
        """Create necessary indexes for users collection."""
        await self.users.create_index("username", unique=True)
        await self.users.create_index("email", unique=True)
        await self.users.create_index("created_at")
        await self.user_sessions.create_index("user_id")
        await self.user_sessions.create_index("expires_at", expireAfterSeconds=0)

    async def create_user(
        self,
        username: str,
        email: str,
        password: str,
        role: Role = Role.VIEWER,
        full_name: Optional[str] = None,
    ) -> Optional[str]:
        """Create a new user."""
        try:
            # Check if user exists
            existing = await self.users.find_one(
                {"$or": [{"username": username}, {"email": email}]}
            )
            if existing:
                logger.warning(f"User already exists: {username}")
                return None

            # Hash password
            hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

            user_doc = {
                "username": username,
                "email": email,
                "password": hashed_password,
                "role": role.value,
                "full_name": full_name or username,
                "is_active": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "last_login": None,
                "login_count": 0,
                "mfa_enabled": False,
                "mfa_secret": None,
            }

            result = await self.users.insert_one(user_doc)
            logger.info(f"Created user: {username}")
            return str(result.inserted_id)

        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return None

    async def get_user(self, user_id: str) -> Optional[dict]:
        """Get user by ID."""
        try:
            return await self.users.find_one({"_id": ObjectId(user_id)})
        except Exception as e:
            logger.error(f"Error getting user: {e}")
            return None

    async def get_user_by_username(self, username: str) -> Optional[dict]:
        """Get user by username."""
        return await self.users.find_one({"username": username})

    async def verify_password(self, user_id: str, password: str) -> bool:
        """Verify user password."""
        try:
            user = await self.get_user(user_id)
            if not user:
                return False
            return bcrypt.checkpw(password.encode("utf-8"), user["password"])
        except Exception as e:
            logger.error(f"Error verifying password: {e}")
            return False

    async def update_user_role(self, user_id: str, new_role: Role) -> bool:
        """Update user role."""
        try:
            result = await self.users.update_one(
                {"_id": ObjectId(user_id)},
                {
                    "$set": {
                        "role": new_role.value,
                        "updated_at": datetime.utcnow(),
                    }
                },
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error updating user role: {e}")
            return False

    async def deactivate_user(self, user_id: str) -> bool:
        """Deactivate a user."""
        try:
            result = await self.users.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {"is_active": False, "updated_at": datetime.utcnow()}},
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error deactivating user: {e}")
            return False

    async def update_last_login(self, user_id: str) -> bool:
        """Update user's last login time."""
        try:
            result = await self.users.update_one(
                {"_id": ObjectId(user_id)},
                {
                    "$set": {"last_login": datetime.utcnow()},
                    "$inc": {"login_count": 1},
                },
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error updating last login: {e}")
            return False

    async def list_users(self, skip: int = 0, limit: int = 50) -> List[dict]:
        """List all users with pagination."""
        try:
            return await self.users.find({}).skip(skip).limit(limit).to_list(limit)
        except Exception as e:
            logger.error(f"Error listing users: {e}")
            return []

    async def get_user_role(self, user_id: str) -> Optional[Role]:
        """Get user's role."""
        try:
            user = await self.get_user(user_id)
            if user:
                return Role(user.get("role", Role.VIEWER.value))
            return None
        except Exception as e:
            logger.error(f"Error getting user role: {e}")
            return None

    async def has_permission(self, user_id: str, permission: Permission) -> bool:
        """Check if user has permission."""
        try:
            from security.rbac import has_permission

            role = await self.get_user_role(user_id)
            if not role:
                return False
            return has_permission(role, permission)
        except Exception as e:
            logger.error(f"Error checking permission: {e}")
            return False
