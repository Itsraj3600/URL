"""
Secrets management for CINE3600.

Handles encryption, storage, and rotation of sensitive configuration.
"""

import os
import logging
from datetime import datetime
from typing import Optional
from cryptography.fernet import Fernet
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

logger = logging.getLogger(__name__)

# Get or generate encryption key
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")
if not ENCRYPTION_KEY:
    logger.warning(
        "ENCRYPTION_KEY not set. Generating new key - set this in .env for production"
    )
    ENCRYPTION_KEY = Fernet.generate_key().decode()

CIPHER = Fernet(ENCRYPTION_KEY.encode() if isinstance(ENCRYPTION_KEY, str) else ENCRYPTION_KEY)


class SecretsManager:
    """Manage encrypted secrets and sensitive configuration."""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.secrets = db.secrets
        self.secret_audit = db.secret_audit

    async def create_indexes(self):
        """Create necessary indexes."""
        await self.secrets.create_index("key", unique=True)
        await self.secrets.create_index("created_at")
        await self.secrets.create_index("accessed_at")
        await self.secret_audit.create_index("secret_key")
        await self.secret_audit.create_index("created_at")

    def _encrypt(self, value: str) -> str:
        """Encrypt a string value."""
        return CIPHER.encrypt(value.encode()).decode()

    def _decrypt(self, encrypted_value: str) -> str:
        """Decrypt a string value."""
        return CIPHER.decrypt(encrypted_value.encode()).decode()

    async def set_secret(
        self,
        key: str,
        value: str,
        description: str = "",
        rotate_after_days: Optional[int] = None,
    ) -> bool:
        """Set or update a secret."""
        try:
            encrypted_value = self._encrypt(value)

            secret_doc = {
                "key": key,
                "value": encrypted_value,
                "description": description,
                "created_at": datetime.utcnow(),
                "accessed_at": None,
                "rotate_after_days": rotate_after_days,
                "is_active": True,
            }

            # Try to update existing, otherwise insert
            result = await self.secrets.update_one(
                {"key": key},
                {"$set": secret_doc},
                upsert=True,
            )

            logger.info(f"Secret stored: {key}")
            return True
        except Exception as e:
            logger.error(f"Error setting secret: {e}")
            return False

    async def get_secret(self, key: str) -> Optional[str]:
        """Get a decrypted secret."""
        try:
            secret_doc = await self.secrets.find_one(
                {"key": key, "is_active": True}
            )

            if not secret_doc:
                logger.warning(f"Secret not found: {key}")
                return None

            # Update accessed time
            await self.secrets.update_one(
                {"_id": secret_doc["_id"]},
                {"$set": {"accessed_at": datetime.utcnow()}},
            )

            # Log access
            await self.secret_audit.insert_one(
                {
                    "secret_key": key,
                    "action": "accessed",
                    "created_at": datetime.utcnow(),
                }
            )

            return self._decrypt(secret_doc["value"])
        except Exception as e:
            logger.error(f"Error getting secret: {e}")
            return None

    async def delete_secret(self, key: str) -> bool:
        """Delete a secret (soft delete)."""
        try:
            result = await self.secrets.update_one(
                {"key": key},
                {
                    "$set": {
                        "is_active": False,
                        "deleted_at": datetime.utcnow(),
                    }
                },
            )

            if result.modified_count > 0:
                await self.secret_audit.insert_one(
                    {
                        "secret_key": key,
                        "action": "deleted",
                        "created_at": datetime.utcnow(),
                    }
                )
                logger.info(f"Secret deleted: {key}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting secret: {e}")
            return False

    async def rotate_secret(self, key: str, new_value: str) -> bool:
        """Rotate a secret to a new value."""
        try:
            old_secret = await self.secrets.find_one({"key": key})
            if not old_secret:
                return False

            # Archive old secret
            archive_key = f"{key}_archived_{datetime.utcnow().timestamp()}"
            await self.set_secret(
                archive_key,
                self._decrypt(old_secret["value"]),
                f"Archived from {key}",
            )

            # Update with new value
            encrypted_value = self._encrypt(new_value)
            await self.secrets.update_one(
                {"key": key},
                {
                    "$set": {
                        "value": encrypted_value,
                        "rotated_at": datetime.utcnow(),
                    }
                },
            )

            await self.secret_audit.insert_one(
                {
                    "secret_key": key,
                    "action": "rotated",
                    "created_at": datetime.utcnow(),
                }
            )

            logger.info(f"Secret rotated: {key}")
            return True
        except Exception as e:
            logger.error(f"Error rotating secret: {e}")
            return False

    async def list_secrets(self) -> list:
        """List all secret keys (without values)."""
        try:
            secrets = await self.secrets.find(
                {"is_active": True},
                {"value": 0},  # Exclude encrypted values
            ).to_list(None)
            return secrets
        except Exception as e:
            logger.error(f"Error listing secrets: {e}")
            return []

    async def get_audit_log(self, key: str, limit: int = 50) -> list:
        """Get audit log for a secret."""
        try:
            return (
                await self.secret_audit.find({"secret_key": key})
                .sort("created_at", -1)
                .limit(limit)
                .to_list(limit)
            )
        except Exception as e:
            logger.error(f"Error getting audit log: {e}")
            return []

    async def check_rotation_needed(self) -> list:
        """Find secrets that need rotation."""
        try:
            from datetime import timedelta

            secrets_to_rotate = []
            secrets = await self.secrets.find(
                {
                    "is_active": True,
                    "rotate_after_days": {"$ne": None},
                }
            ).to_list(None)

            for secret in secrets:
                days_since = (
                    datetime.utcnow() - secret.get("rotated_at", secret["created_at"])
                ).days
                if days_since >= secret["rotate_after_days"]:
                    secrets_to_rotate.append(secret["key"])

            return secrets_to_rotate
        except Exception as e:
            logger.error(f"Error checking rotation needed: {e}")
            return []
