"""
Audit logging for CINE3600.

Immutable audit trail for security and compliance.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from enum import Enum
from motor.motor_asyncio import AsyncIOMotorDatabase

logger = logging.getLogger(__name__)


class AuditAction(Enum):
    """Audit trail actions."""
    # User actions
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    USER_CREATED = "user_created"
    USER_UPDATED = "user_updated"
    USER_DELETED = "user_deleted"
    USER_ROLE_CHANGED = "user_role_changed"
    
    # API actions
    API_KEY_CREATED = "api_key_created"
    API_KEY_REVOKED = "api_key_revoked"
    API_KEY_USED = "api_key_used"
    
    # Admin actions
    ADMIN_SETTINGS_CHANGED = "admin_settings_changed"
    BACKUP_CREATED = "backup_created"
    BACKUP_RESTORED = "backup_restored"
    
    # Security events
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    FAILED_LOGIN = "failed_login"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"


class AuditLogger:
    """Immutable audit trail for compliance."""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.audit_logs = db.audit_logs

    async def create_indexes(self):
        """Create necessary indexes."""
        await self.audit_logs.create_index("user_id")
        await self.audit_logs.create_index("action")
        await self.audit_logs.create_index("created_at")
        await self.audit_logs.create_index("severity")
        # TTL index for logs older than 365 days
        await self.audit_logs.create_index("created_at", expireAfterSeconds=31536000)

    async def log(
        self,
        action: AuditAction,
        user_id: str,
        severity: str = "info",
        details: Optional[Dict] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> bool:
        """Log an audit event (immutable)."""
        try:
            audit_doc = {
                "action": action.value,
                "user_id": user_id,
                "severity": severity,
                "details": details or {},
                "ip_address": ip_address,
                "user_agent": user_agent,
                "created_at": datetime.utcnow(),
                "is_archived": False,
            }

            result = await self.audit_logs.insert_one(audit_doc)
            logger.debug(f"Audit logged: {action.value} by {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error logging audit: {e}")
            return False

    async def get_logs(
        self,
        user_id: Optional[str] = None,
        action: Optional[AuditAction] = None,
        severity: Optional[str] = None,
        days: int = 30,
        limit: int = 100,
    ) -> List[Dict]:
        """Get audit logs with filters."""
        try:
            query = {}
            
            if user_id:
                query["user_id"] = user_id
            if action:
                query["action"] = action.value
            if severity:
                query["severity"] = severity
            
            # Filter by date
            cutoff = datetime.utcnow() - timedelta(days=days)
            query["created_at"] = {"$gte": cutoff}

            logs = (
                await self.audit_logs.find(query)
                .sort("created_at", -1)
                .limit(limit)
                .to_list(limit)
            )
            return logs
        except Exception as e:
            logger.error(f"Error getting audit logs: {e}")
            return []

    async def get_user_activity(
        self,
        user_id: str,
        days: int = 7,
    ) -> Dict:
        """Get activity summary for a user."""
        try:
            cutoff = datetime.utcnow() - timedelta(days=days)
            
            logs = await self.audit_logs.find(
                {
                    "user_id": user_id,
                    "created_at": {"$gte": cutoff},
                }
            ).to_list(None)

            # Count by action
            action_counts = {}
            severity_counts = {"info": 0, "warning": 0, "critical": 0}
            
            for log in logs:
                action = log.get("action", "unknown")
                action_counts[action] = action_counts.get(action, 0) + 1
                
                severity = log.get("severity", "info")
                if severity in severity_counts:
                    severity_counts[severity] += 1

            return {
                "user_id": user_id,
                "total_events": len(logs),
                "actions": action_counts,
                "severities": severity_counts,
                "last_activity": logs[0]["created_at"] if logs else None,
            }
        except Exception as e:
            logger.error(f"Error getting user activity: {e}")
            return {}

    async def get_suspicious_activities(self, hours: int = 24) -> List[Dict]:
        """Get suspicious or critical activities."""
        try:
            cutoff = datetime.utcnow() - timedelta(hours=hours)
            
            logs = (
                await self.audit_logs.find(
                    {
                        "created_at": {"$gte": cutoff},
                        "$or": [
                            {"severity": "critical"},
                            {"action": AuditAction.UNAUTHORIZED_ACCESS.value},
                            {"action": AuditAction.FAILED_LOGIN.value},
                            {"action": AuditAction.SUSPICIOUS_ACTIVITY.value},
                        ],
                    }
                )
                .sort("created_at", -1)
                .limit(100)
                .to_list(100)
            )
            
            return logs
        except Exception as e:
            logger.error(f"Error getting suspicious activities: {e}")
            return []

    async def archive_old_logs(self, days: int = 365) -> int:
        """Mark very old logs as archived for optimization."""
        try:
            cutoff = datetime.utcnow() - timedelta(days=days)
            result = await self.audit_logs.update_many(
                {
                    "created_at": {"$lt": cutoff},
                    "is_archived": False,
                },
                {"$set": {"is_archived": True}},
            )
            logger.info(f"Archived {result.modified_count} old audit logs")
            return result.modified_count
        except Exception as e:
            logger.error(f"Error archiving logs: {e}")
            return 0

    async def export_logs(
        self,
        user_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[Dict]:
        """Export audit logs for compliance reporting."""
        try:
            query = {}
            
            if user_id:
                query["user_id"] = user_id
            
            if start_date or end_date:
                date_query = {}
                if start_date:
                    date_query["$gte"] = start_date
                if end_date:
                    date_query["$lte"] = end_date
                query["created_at"] = date_query

            logs = (
                await self.audit_logs.find(query)
                .sort("created_at", -1)
                .to_list(None)
            )
            
            return logs
        except Exception as e:
            logger.error(f"Error exporting logs: {e}")
            return []
