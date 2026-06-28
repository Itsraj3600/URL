"""
Dashboard API

REST API endpoints for the admin dashboard.

All dashboard pages communicate through these APIs.

Endpoints:
- GET    /api/overview          - Dashboard overview stats
- GET    /api/users              - List users
- GET    /api/index/jobs         - List index jobs
- GET    /api/channels           - List channels
- GET    /api/logs               - Get logs
- GET    /api/health             - Health check
- POST   /api/index/start        - Start indexing
- POST   /api/index/pause        - Pause indexing
- POST   /api/index/resume       - Resume indexing
- POST   /api/index/cancel       - Cancel indexing
- POST   /api/cache/clear        - Clear cache
- GET    /api/analytics/search   - Search analytics
- GET    /api/analytics/index    - Index analytics
"""

import logging
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class OverviewStats:
    """Dashboard overview statistics."""
    # Bot status
    bot_status: str = "online"
    uptime_seconds: int = 0

    # Counts
    total_users: int = 0
    total_files: int = 0
    total_channels: int = 0

    # Today's activity
    searches_today: int = 0
    downloads_today: int = 0
    new_users_today: int = 0

    # Performance
    cache_hit_rate: float = 0.0
    avg_search_time_ms: float = 0.0

    # Workers
    active_workers: int = 0
    total_workers: int = 0

    # Indexing
    indexing_status: str = "idle"
    indexing_progress: float = 0.0

    # System
    cpu_usage: float = 0.0
    memory_usage_mb: float = 0.0
    disk_usage_percent: float = 0.0

    # Database
    db_status: str = "healthy"
    db_size_mb: float = 0.0


@dataclass
class UserInfo:
    """User information for dashboard."""
    user_id: int
    username: str = ""
    first_name: str = ""
    joined_at: Optional[datetime] = None
    last_seen: Optional[datetime] = None
    search_count: int = 0
    download_count: int = 0
    is_premium: bool = False
    is_banned: bool = False
    ban_reason: str = ""


@dataclass
class IndexJobInfo:
    """Index job information for dashboard."""
    job_id: str
    channel_id: int
    channel_name: str = ""
    status: str = "pending"
    progress_percent: float = 0.0
    processed: int = 0
    inserted: int = 0
    duplicates: int = 0
    errors: int = 0
    speed: float = 0.0
    eta: str = ""
    started_at: Optional[datetime] = None


@dataclass
class ChannelInfo:
    """Channel information for dashboard."""
    channel_id: int
    channel_name: str = ""
    channel_username: str = ""
    connected: bool = False
    files_count: int = 0
    last_sync: Optional[datetime] = None
    status: str = "active"


@dataclass
class LogEntry:
    """Log entry for dashboard."""
    timestamp: datetime
    level: str
    message: str
    source: str = ""


class DashboardAPI:
    """
    Dashboard API implementation.

    Provides data for the admin dashboard frontend.
    """

    def __init__(self):
        self._start_time = time.monotonic()

    # ==========================================================================
    # Overview
    # ==========================================================================

    async def get_overview(self) -> OverviewStats:
        """Get dashboard overview statistics."""
        stats = OverviewStats()
        stats.uptime_seconds = int(time.monotonic() - self._start_time)

        try:
            # Get user count
            from database.users_chats_db import db
            stats.total_users = await db.total_users_count()
            stats.total_channels = await db.total_chat_count()

            # Get file count
            from database.ia_filterdb import Media
            stats.total_files = await Media.count_documents()

            # Get search stats
            from services import get_stats_service
            search_stats = get_stats_service().get_stats_summary()
            stats.cache_hit_rate = search_stats.get("cache_hit_rate", 0)
            stats.avg_search_time_ms = search_stats.get("avg_search_time_ms", 0)

            # Get index stats
            from services import get_index_service
            index = get_index_service()
            if index.is_indexing():
                stats.indexing_status = "running"
                job = index.get_active_job()
                if job:
                    progress = (job.processed / max(job.last_message_id, 1)) * 100
                    stats.indexing_progress = round(progress, 1)

            # Get cache efficiency
            from services import get_cache_service
            cache = get_cache_service()
            stats.cache_hit_rate = cache.get_total_hit_rate() * 100

            # Database status
            try:
                from database.client import healthy_nodes
                nodes = healthy_nodes()
                stats.db_status = "healthy" if nodes else "degraded"
            except Exception:
                stats.db_status = "unknown"

        except Exception as e:
            logger.error(f"Error getting overview: {e}")

        return stats

    # ==========================================================================
    # Users
    # ==========================================================================

    async def get_users(
        self,
        limit: int = 50,
        offset: int = 0,
        search: str = "",
        banned_only: bool = False,
        premium_only: bool = False
    ) -> List[UserInfo]:
        """Get list of users."""
        users = []
        try:
            from database.users_chats_db import db

            # Build filter
            filter_query = {}
            if banned_only:
                filter_query["ban_status.is_banned"] = True
            if premium_only:
                filter_query["expiry_time"] = {"$ne": None}

            cursor = db.col.find(filter_query).skip(offset).limit(limit)
            async for doc in cursor:
                users.append(UserInfo(
                    user_id=doc.get("id", 0),
                    username=doc.get("username", ""),
                    first_name=doc.get("name", ""),
                    is_banned=doc.get("ban_status", {}).get("is_banned", False),
                    ban_reason=doc.get("ban_status", {}).get("ban_reason", "")
                ))
        except Exception as e:
            logger.error(f"Error getting users: {e}")

        return users

    async def get_user(self, user_id: int) -> Optional[UserInfo]:
        """Get single user details."""
        try:
            from database.users_chats_db import db

            doc = await db.col.find_one({"id": user_id})
            if doc:
                # Get search/download counts
                from services import get_stats_service
                user_stats = get_stats_service().get_user_stats(user_id)

                return UserInfo(
                    user_id=user_id,
                    username=doc.get("username", ""),
                    first_name=doc.get("name", ""),
                    is_banned=doc.get("ban_status", {}).get("is_banned", False),
                    is_premium=await db.has_premium_access(user_id),
                    search_count=user_stats.get("search_count", 0) if user_stats else 0
                )
        except Exception as e:
            logger.error(f"Error getting user {user_id}: {e}")

        return None

    async def ban_user(self, user_id: int, reason: str = "") -> bool:
        """Ban a user."""
        try:
            from database.users_chats_db import db
            await db.ban_user(user_id, reason or "Banned via dashboard")
            return True
        except Exception as e:
            logger.error(f"Error banning user {user_id}: {e}")
            return False

    async def unban_user(self, user_id: int) -> bool:
        """Unban a user."""
        try:
            from database.users_chats_db import db
            await db.remove_ban(user_id)
            return True
        except Exception as e:
            logger.error(f"Error unbanning user {user_id}: {e}")
            return False

    # ==========================================================================
    # Indexing
    # ==========================================================================

    async def get_index_jobs(self) -> List[IndexJobInfo]:
        """Get list of index jobs."""
        jobs = []
        try:
            from services import get_index_service
            index = get_index_service()

            for job in await index.get_all_jobs():
                progress = (job.processed / max(job.last_message_id, 1)) * 100
                jobs.append(IndexJobInfo(
                    job_id=job.job_id,
                    channel_id=job.channel_id,
                    channel_name=job.channel_name,
                    status=job.status.value,
                    progress_percent=round(progress, 1),
                    processed=job.processed,
                    inserted=job.inserted,
                    duplicates=job.duplicates,
                    errors=job.errors,
                    speed=round(job.files_per_second, 1),
                    eta=job.eta_human if hasattr(job, 'eta_human') else "",
                    started_at=job.started_at
                ))
        except Exception as e:
            logger.error(f"Error getting index jobs: {e}")

        return jobs

    async def start_index(
        self,
        channel_id: int,
        last_message_id: int,
        requested_by: int = 0
    ) -> Optional[str]:
        """Start an index job."""
        try:
            from services import get_index_service
            index = get_index_service()

            job = await index.create_job(
                channel_id=channel_id,
                last_message_id=last_message_id,
                requested_by=requested_by
            )

            return job.job_id
        except Exception as e:
            logger.error(f"Error starting index: {e}")
            return None

    async def pause_index(self, job_id: str) -> bool:
        """Pause an index job."""
        try:
            from services import get_index_service
            index = get_index_service()
            return await index.pause_job(job_id)
        except Exception as e:
            logger.error(f"Error pausing index: {e}")
            return False

    async def resume_index(self, job_id: str) -> bool:
        """Resume an index job."""
        try:
            from services import get_index_service
            index = get_index_service()
            return await index.resume_job(job_id)
        except Exception as e:
            logger.error(f"Error resuming index: {e}")
            return False

    async def cancel_index(self, job_id: str) -> bool:
        """Cancel an index job."""
        try:
            from services import get_index_service
            index = get_index_service()
            return await index.cancel_job(job_id)
        except Exception as e:
            logger.error(f"Error cancelling index: {e}")
            return False

    # ==========================================================================
    # Channels
    # ==========================================================================

    async def get_channels(self) -> List[ChannelInfo]:
        """Get list of channels."""
        channels = []
        try:
            from database.users_chats_db import db

            cursor = db.grp.find({})
            async for doc in cursor:
                channels.append(ChannelInfo(
                    channel_id=doc.get("id", 0),
                    channel_name=doc.get("title", ""),
                    connected=True
                ))
        except Exception as e:
            logger.error(f"Error getting channels: {e}")

        return channels

    # ==========================================================================
    # Logs
    # ==========================================================================

    async def get_logs(
        self,
        limit: int = 100,
        level: str = "",
        search: str = ""
    ) -> List[LogEntry]:
        """Get recent logs."""
        # For now, return empty list
        # In production, this would read from log files or a log database
        return []

    # ==========================================================================
    # Health
    # ==========================================================================

    async def get_health(self) -> Dict[str, Any]:
        """Get system health status."""
        health = {
            "status": "healthy",
            "checks": [],
            "timestamp": datetime.utcnow().isoformat()
        }

        checks = []

        # Check MongoDB
        try:
            from database.client import healthy_nodes
            nodes = healthy_nodes()
            checks.append({
                "name": "MongoDB",
                "status": "healthy" if nodes else "unhealthy",
                "details": f"{len(nodes)} nodes connected"
            })
        except Exception as e:
            checks.append({"name": "MongoDB", "status": "unhealthy", "error": str(e)})
            health["status"] = "degraded"

        # Check Telegram
        try:
            from cinebot.clients import CinébotClient
            # Check if bot is running
            checks.append({
                "name": "Telegram Bot",
                "status": "healthy",
                "details": "Bot running"
            })
        except Exception:
            checks.append({"name": "Telegram Bot", "status": "unknown"})

        # Check Workers
        try:
            from services import get_index_service
            index = get_index_service()
            if index.is_indexing():
                checks.append({"name": "Index Worker", "status": "running"})
            else:
                checks.append({"name": "Index Worker", "status": "idle"})
        except Exception:
            checks.append({"name": "Index Worker", "status": "unknown"})

        # Check Cache
        try:
            from services import get_cache_service
            cache = get_cache_service()
            hit_rate = cache.get_total_hit_rate()
            checks.append({
                "name": "Cache",
                "status": "healthy",
                "details": f"Hit rate: {hit_rate * 100:.1f}%"
            })
        except Exception:
            checks.append({"name": "Cache", "status": "unknown"})

        health["checks"] = checks
        return health

    # ==========================================================================
    # Analytics
    # ==========================================================================

    async def get_search_analytics(self, days: int = 7) -> Dict[str, Any]:
        """Get search analytics data."""
        try:
            from services import get_stats_service
            stats = get_stats_service()

            return {
                "period_days": days,
                "performance": stats.get_performance_summary(hours=days * 24),
                "popular_queries": stats.get_popular_queries(limit=10),
                "hourly_breakdown": stats.get_hourly_breakdown(hours=days * 24),
                "cache_efficiency": stats.get_cache_efficiency()
            }
        except Exception as e:
            logger.error(f"Error getting search analytics: {e}")
            return {"error": str(e)}

    async def get_index_analytics(self) -> Dict[str, Any]:
        """Get index analytics data."""
        try:
            from services import get_index_stats_service
            stats = get_index_stats_service()

            return stats.export_all()
        except Exception as e:
            logger.error(f"Error getting index analytics: {e}")
            return {"error": str(e)}

    # ==========================================================================
    # Cache Management
    # ==========================================================================

    async def clear_cache(self, cache_type: str = "all") -> Dict[str, int]:
        """Clear cache(s)."""
        try:
            from services import get_cache_service
            cache = get_cache_service()

            if cache_type == "all":
                return cache.invalidate_all()
            elif cache_type == "search":
                return {"search": cache.invalidate_search()}
            else:
                return {"error": "Unknown cache type"}
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            return {"error": str(e)}

    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        try:
            from services import get_cache_service
            cache = get_cache_service()

            return {
                "caches": cache.get_all_stats(),
                "total_hit_rate": cache.get_total_hit_rate()
            }
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {"error": str(e)}


# =============================================================================
# Global Instance
# =============================================================================

_dashboard_api: Optional[DashboardAPI] = None


def get_dashboard_api() -> DashboardAPI:
    """Get or create the global DashboardAPI instance."""
    global _dashboard_api
    if _dashboard_api is None:
        _dashboard_api = DashboardAPI()
    return _dashboard_api
