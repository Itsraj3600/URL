"""
JWT-based authentication for CINE3600.

Handles token generation, validation, and session management.
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict
import jwt
from motor.motor_asyncio import AsyncIOMotorDatabase

logger = logging.getLogger(__name__)

# JWT configuration
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "1440"))  # 24 hours
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("JWT_REFRESH_DAYS", "7"))  # 7 days


class JWTAuth:
    """JWT authentication manager."""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.sessions = db.user_sessions

    async def create_indexes(self):
        """Create necessary indexes."""
        await self.sessions.create_index("user_id")
        await self.sessions.create_index("token_hash", unique=True)
        await self.sessions.create_index("expires_at", expireAfterSeconds=0)

    def create_access_token(self, user_id: str, role: str) -> str:
        """Create JWT access token."""
        try:
            payload = {
                "user_id": user_id,
                "role": role,
                "type": "access",
                "iat": datetime.utcnow(),
                "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
            }
            token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
            return token
        except Exception as e:
            logger.error(f"Error creating access token: {e}")
            return None

    def create_refresh_token(self, user_id: str) -> str:
        """Create JWT refresh token."""
        try:
            payload = {
                "user_id": user_id,
                "type": "refresh",
                "iat": datetime.utcnow(),
                "exp": datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
            }
            token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
            return token
        except Exception as e:
            logger.error(f"Error creating refresh token: {e}")
            return None

    async def verify_token(self, token: str) -> Optional[Dict]:
        """Verify JWT token."""
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            return None
        except Exception as e:
            logger.error(f"Error verifying token: {e}")
            return None

    async def save_session(
        self, user_id: str, access_token: str, refresh_token: str, ip_address: str
    ) -> bool:
        """Save session to database."""
        try:
            import hashlib

            token_hash = hashlib.sha256(access_token.encode()).hexdigest()

            session_doc = {
                "user_id": user_id,
                "token_hash": token_hash,
                "refresh_token": refresh_token,
                "ip_address": ip_address,
                "user_agent": "",
                "created_at": datetime.utcnow(),
                "expires_at": datetime.utcnow()
                + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
                "is_active": True,
            }

            await self.sessions.insert_one(session_doc)
            logger.info(f"Session created for user: {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error saving session: {e}")
            return False

    async def validate_session(self, user_id: str, token: str) -> bool:
        """Validate session exists and is active."""
        try:
            import hashlib

            token_hash = hashlib.sha256(token.encode()).hexdigest()

            session = await self.sessions.find_one(
                {
                    "user_id": user_id,
                    "token_hash": token_hash,
                    "is_active": True,
                    "expires_at": {"$gt": datetime.utcnow()},
                }
            )
            return session is not None
        except Exception as e:
            logger.error(f"Error validating session: {e}")
            return False

    async def revoke_session(self, user_id: str, token: str) -> bool:
        """Revoke a session."""
        try:
            import hashlib

            token_hash = hashlib.sha256(token.encode()).hexdigest()

            result = await self.sessions.update_one(
                {"user_id": user_id, "token_hash": token_hash},
                {"$set": {"is_active": False}},
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error revoking session: {e}")
            return False

    async def revoke_all_sessions(self, user_id: str) -> bool:
        """Revoke all sessions for a user."""
        try:
            result = await self.sessions.update_many(
                {"user_id": user_id},
                {"$set": {"is_active": False}},
            )
            logger.info(f"Revoked {result.modified_count} sessions for user: {user_id}")
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error revoking all sessions: {e}")
            return False

    async def refresh_access_token(self, refresh_token: str) -> Optional[str]:
        """Refresh access token using refresh token."""
        try:
            payload = await self.verify_token(refresh_token)
            if not payload or payload.get("type") != "refresh":
                return None

            user_id = payload.get("user_id")
            if not user_id:
                return None

            # Verify session still exists
            session = await self.sessions.find_one(
                {
                    "user_id": user_id,
                    "refresh_token": refresh_token,
                    "is_active": True,
                }
            )

            if not session:
                return None

            # Get user role from database
            from database.user_db import UserDB

            user_db = UserDB(self.db)
            role = await user_db.get_user_role(user_id)
            if not role:
                return None

            return self.create_access_token(user_id, role.value)
        except Exception as e:
            logger.error(f"Error refreshing token: {e}")
            return None
