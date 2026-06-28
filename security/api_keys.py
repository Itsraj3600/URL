"""
API Key management for CINE3600.

Handles generation, validation, and lifecycle of API keys.
"""

import os
import logging
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional, List, Tuple
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

logger = logging.getLogger(__name__)


class APIKeyManager:
    """API key manager for service-to-service authentication."""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.api_keys = db.api_keys
        self.key_usage = db.api_key_usage

    async def create_indexes(self):
        """Create necessary indexes."""
        await self.api_keys.create_index("key_hash", unique=True)
        await self.api_keys.create_index("user_id")
        await self.api_keys.create_index("created_at")
        await self.api_keys.create_index("expires_at")
        await self.key_usage.create_index("api_key_id")
        await self.key_usage.create_index("created_at")

    def generate_key(self) -> Tuple[str, str]:
        """Generate a new API key and its hash.
        
        Returns:
            Tuple of (raw_key, key_hash)
        """
        raw_key = f"cine_{secrets.token_urlsafe(32)}"
        key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
        return raw_key, key_hash

    async def create_api_key(
        self,
        user_id: str,
        name: str,
        role: str = "api",
        expires_in_days: Optional[int] = None,
    ) -> Optional[str]:
        """Create a new API key for a user.
        
        Args:
            user_id: User ID creating the key
            name: Human-readable name for the key
            role: Role to assign to this key
            expires_in_days: Days until expiration (None = never expires)
            
        Returns:
            Raw API key (shown only once)
        """
        try:
            raw_key, key_hash = self.generate_key()

            api_key_doc = {
                "user_id": user_id,
                "name": name,
                "key_hash": key_hash,
                "role": role,
                "created_at": datetime.utcnow(),
                "expires_at": (
                    datetime.utcnow() + timedelta(days=expires_in_days)
                    if expires_in_days
                    else None
                ),
                "is_active": True,
                "last_used": None,
                "usage_count": 0,
            }

            result = await self.api_keys.insert_one(api_key_doc)
            logger.info(f"Created API key: {name} for user: {user_id}")
            return raw_key
        except Exception as e:
            logger.error(f"Error creating API key: {e}")
            return None

    async def validate_api_key(self, api_key: str) -> Optional[dict]:
        """Validate an API key.
        
        Returns:
            Key document if valid, None otherwise
        """
        try:
            key_hash = hashlib.sha256(api_key.encode()).hexdigest()

            key_doc = await self.api_keys.find_one(
                {
                    "key_hash": key_hash,
                    "is_active": True,
                    "$or": [
                        {"expires_at": None},
                        {"expires_at": {"$gt": datetime.utcnow()}},
                    ],
                }
            )

            if key_doc:
                # Update last used and increment usage
                await self.api_keys.update_one(
                    {"_id": key_doc["_id"]},
                    {
                        "$set": {"last_used": datetime.utcnow()},
                        "$inc": {"usage_count": 1},
                    },
                )

                # Record usage
                await self.key_usage.insert_one(
                    {
                        "api_key_id": str(key_doc["_id"]),
                        "user_id": key_doc["user_id"],
                        "created_at": datetime.utcnow(),
                    }
                )

            return key_doc
        except Exception as e:
            logger.error(f"Error validating API key: {e}")
            return None

    async def revoke_api_key(self, key_id: str) -> bool:
        """Revoke an API key."""
        try:
            result = await self.api_keys.update_one(
                {"_id": ObjectId(key_id)},
                {"$set": {"is_active": False}},
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error revoking API key: {e}")
            return False

    async def list_user_keys(self, user_id: str) -> List[dict]:
        """List all API keys for a user."""
        try:
            keys = await self.api_keys.find({"user_id": user_id}).to_list(None)
            # Remove hashes from response
            for key in keys:
                del key["key_hash"]
            return keys
        except Exception as e:
            logger.error(f"Error listing API keys: {e}")
            return []

    async def get_key_usage(self, key_id: str, days: int = 7) -> int:
        """Get usage count for an API key in the last N days."""
        try:
            cutoff = datetime.utcnow() - timedelta(days=days)
            count = await self.key_usage.count_documents(
                {
                    "api_key_id": key_id,
                    "created_at": {"$gt": cutoff},
                }
            )
            return count
        except Exception as e:
            logger.error(f"Error getting key usage: {e}")
            return 0

    async def rotate_key(self, key_id: str) -> Optional[str]:
        """Rotate an API key (revoke old, create new)."""
        try:
            old_key = await self.api_keys.find_one({"_id": ObjectId(key_id)})
            if not old_key:
                return None

            # Revoke old key
            await self.revoke_api_key(key_id)

            # Create new key with same properties
            new_raw_key = await self.create_api_key(
                user_id=old_key["user_id"],
                name=f"{old_key['name']} (rotated)",
                role=old_key["role"],
                expires_in_days=(
                    int(
                        (old_key["expires_at"] - datetime.utcnow()).days
                    )
                    if old_key["expires_at"]
                    else None
                ),
            )

            logger.info(f"Rotated API key: {key_id}")
            return new_raw_key
        except Exception as e:
            logger.error(f"Error rotating API key: {e}")
            return None

    async def cleanup_expired_keys(self) -> int:
        """Remove expired keys older than 30 days."""
        try:
            cutoff = datetime.utcnow() - timedelta(days=30)
            result = await self.api_keys.delete_many(
                {
                    "expires_at": {"$lt": cutoff},
                    "is_active": False,
                }
            )
            logger.info(f"Cleaned up {result.deleted_count} expired API keys")
            return result.deleted_count
        except Exception as e:
            logger.error(f"Error cleaning up expired keys: {e}")
            return 0
