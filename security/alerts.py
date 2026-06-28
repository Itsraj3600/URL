"""
Security alerts for CINE3600.

Detects and alerts on suspicious activities and security events.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase

logger = logging.getLogger(__name__)


class SecurityAlerts:
    """Monitor and alert on security events."""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.alerts = db.security_alerts
        self.failed_logins = db.failed_login_attempts

    async def create_indexes(self):
        """Create necessary indexes."""
        await self.alerts.create_index("severity")
        await self.alerts.create_index("created_at")
        await self.alerts.create_index("is_resolved")
        await self.failed_logins.create_index("user_id")
        await self.failed_logins.create_index("ip_address")
        await self.failed_logins.create_index("created_at")

    async def check_failed_logins(
        self,
        user_id: str,
        ip_address: str,
        threshold: int = 5,
        window_minutes: int = 15,
    ) -> bool:
        """Check for brute force attempts."""
        try:
            cutoff = datetime.utcnow() - timedelta(minutes=window_minutes)
            
            # Record failed attempt
            await self.failed_logins.insert_one(
                {
                    "user_id": user_id,
                    "ip_address": ip_address,
                    "created_at": datetime.utcnow(),
                }
            )

            # Check if threshold exceeded
            count = await self.failed_logins.count_documents(
                {
                    "user_id": user_id,
                    "created_at": {"$gte": cutoff},
                }
            )

            if count >= threshold:
                await self.create_alert(
                    "brute_force_attempt",
                    f"Brute force detected for user {user_id}",
                    "critical",
                    details={
                        "user_id": user_id,
                        "ip_address": ip_address,
                        "attempts": count,
                    },
                )
                return True
            return False
        except Exception as e:
            logger.error(f"Error checking failed logins: {e}")
            return False

    async def check_unusual_locations(
        self,
        user_id: str,
        ip_address: str,
        cache: Optional[dict] = None,
    ) -> bool:
        """Detect login from unusual location."""
        try:
            # Get last login IP
            last_session = await self.db.user_sessions.find_one(
                {"user_id": user_id},
                sort=[("created_at", -1)],
            )

            if last_session:
                last_ip = last_session.get("ip_address")
                if last_ip and last_ip != ip_address:
                    # Check if location changed (simple implementation)
                    await self.create_alert(
                        "unusual_login_location",
                        f"Login from new location for user {user_id}",
                        "warning",
                        details={
                            "user_id": user_id,
                            "previous_ip": last_ip,
                            "new_ip": ip_address,
                        },
                    )
                    return True
            return False
        except Exception as e:
            logger.error(f"Error checking unusual locations: {e}")
            return False

    async def check_api_abuse(
        self,
        api_key_id: str,
        threshold: int = 1000,
        window_minutes: int = 60,
    ) -> bool:
        """Detect API key abuse."""
        try:
            cutoff = datetime.utcnow() - timedelta(minutes=window_minutes)
            
            count = await self.db.api_key_usage.count_documents(
                {
                    "api_key_id": api_key_id,
                    "created_at": {"$gte": cutoff},
                }
            )

            if count > threshold:
                await self.create_alert(
                    "api_key_abuse",
                    f"Excessive API usage detected",
                    "critical",
                    details={
                        "api_key_id": api_key_id,
                        "requests": count,
                        "threshold": threshold,
                    },
                )
                return True
            return False
        except Exception as e:
            logger.error(f"Error checking API abuse: {e}")
            return False

    async def check_privilege_escalation(
        self,
        user_id: str,
        old_role: str,
        new_role: str,
    ) -> bool:
        """Detect privilege escalation."""
        try:
            from security.rbac import get_role_hierarchy_level, Role

            old_level = get_role_hierarchy_level(Role(old_role))
            new_level = get_role_hierarchy_level(Role(new_role))

            if new_level < old_level:  # Lower is higher privilege
                await self.create_alert(
                    "privilege_escalation",
                    f"Privilege escalation for user {user_id}",
                    "critical",
                    details={
                        "user_id": user_id,
                        "old_role": old_role,
                        "new_role": new_role,
                    },
                )
                return True
            return False
        except Exception as e:
            logger.error(f"Error checking privilege escalation: {e}")
            return False

    async def create_alert(
        self,
        alert_type: str,
        message: str,
        severity: str = "warning",
        details: Optional[dict] = None,
    ) -> bool:
        """Create a security alert."""
        try:
            alert_doc = {
                "type": alert_type,
                "message": message,
                "severity": severity,
                "details": details or {},
                "created_at": datetime.utcnow(),
                "is_resolved": False,
                "resolved_at": None,
            }

            await self.alerts.insert_one(alert_doc)
            logger.warning(f"Security alert created: {alert_type} - {severity}")
            return True
        except Exception as e:
            logger.error(f"Error creating alert: {e}")
            return False

    async def get_active_alerts(self, hours: int = 24) -> List[dict]:
        """Get active alerts from the last N hours."""
        try:
            cutoff = datetime.utcnow() - timedelta(hours=hours)
            
            alerts = (
                await self.alerts.find(
                    {
                        "created_at": {"$gte": cutoff},
                        "is_resolved": False,
                    }
                )
                .sort("created_at", -1)
                .to_list(None)
            )
            
            return alerts
        except Exception as e:
            logger.error(f"Error getting active alerts: {e}")
            return []

    async def resolve_alert(self, alert_id: str, notes: Optional[str] = None) -> bool:
        """Resolve a security alert."""
        try:
            from bson import ObjectId
            
            result = await self.alerts.update_one(
                {"_id": ObjectId(alert_id)},
                {
                    "$set": {
                        "is_resolved": True,
                        "resolved_at": datetime.utcnow(),
                        "resolution_notes": notes,
                    }
                },
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error resolving alert: {e}")
            return False

    async def get_alert_summary(self) -> dict:
        """Get summary of recent security alerts."""
        try:
            cutoff_24h = datetime.utcnow() - timedelta(hours=24)
            
            # Count by severity
            alerts_24h = await self.alerts.find(
                {"created_at": {"$gte": cutoff_24h}}
            ).to_list(None)

            severity_counts = {"critical": 0, "warning": 0, "info": 0}
            for alert in alerts_24h:
                severity = alert.get("severity", "info")
                if severity in severity_counts:
                    severity_counts[severity] += 1

            # Unresolved alerts
            unresolved = await self.alerts.count_documents({"is_resolved": False})

            return {
                "total_unresolved": unresolved,
                "alerts_24h": len(alerts_24h),
                "severity_breakdown": severity_counts,
            }
        except Exception as e:
            logger.error(f"Error getting alert summary: {e}")
            return {}

    async def cleanup_old_alerts(self, days: int = 30) -> int:
        """Clean up resolved alerts older than N days."""
        try:
            cutoff = datetime.utcnow() - timedelta(days=days)
            result = await self.alerts.delete_many(
                {
                    "created_at": {"$lt": cutoff},
                    "is_resolved": True,
                }
            )
            logger.info(f"Cleaned up {result.deleted_count} old alerts")
            return result.deleted_count
        except Exception as e:
            logger.error(f"Error cleaning up alerts: {e}")
            return 0
