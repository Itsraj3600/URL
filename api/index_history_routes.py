"""
Index History API Routes

Endpoints for querying and displaying index job history.

Endpoints:
- /api/index/history/jobs - Get recent jobs
- /api/index/history/stats - Get global statistics
- /api/index/history/channel/{id} - Get channel-specific stats
- /api/index/history/job/{id} - Get specific job details
"""

import logging
from typing import Optional
from datetime import datetime

from database.index_history import IndexHistoryDB

logger = logging.getLogger(__name__)


class IndexHistoryRoutes:
    """API routes for index history."""

    @staticmethod
    async def get_recent_jobs(limit: int = 20, skip: int = 0, job_type: Optional[str] = None):
        """Get recent indexing jobs."""
        try:
            jobs = await IndexHistoryDB.get_job_history(
                limit=limit,
                skip=skip,
                job_type=job_type
            )

            # Convert datetime objects to ISO format strings
            for job in jobs:
                if isinstance(job.get("finished"), datetime):
                    job["finished"] = job["finished"].isoformat()
                if isinstance(job.get("created_at"), datetime):
                    job["created_at"] = job["created_at"].isoformat()

            return {
                "status": "success",
                "data": jobs,
                "count": len(jobs)
            }
        except Exception as e:
            logger.error(f"[IndexHistoryAPI] Failed to get recent jobs: {e}")
            return {
                "status": "error",
                "error": str(e),
                "data": []
            }

    @staticmethod
    async def get_job_details(job_id: str):
        """Get details for a specific job."""
        try:
            job = await IndexHistoryDB.get_job(job_id)

            if not job:
                return {
                    "status": "not_found",
                    "error": f"Job {job_id} not found"
                }

            # Convert datetime objects
            if isinstance(job.get("finished"), datetime):
                job["finished"] = job["finished"].isoformat()
            if isinstance(job.get("created_at"), datetime):
                job["created_at"] = job["created_at"].isoformat()

            return {
                "status": "success",
                "data": job
            }
        except Exception as e:
            logger.error(f"[IndexHistoryAPI] Failed to get job {job_id}: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

    @staticmethod
    async def get_global_statistics(days: int = 30):
        """Get global indexing statistics."""
        try:
            stats = await IndexHistoryDB.get_global_stats(days=days)

            return {
                "status": "success",
                "data": stats,
                "generated_at": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"[IndexHistoryAPI] Failed to get global stats: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

    @staticmethod
    async def get_channel_statistics(channel_id: int, days: int = 7):
        """Get statistics for a specific channel."""
        try:
            stats = await IndexHistoryDB.get_stats_by_channel(
                channel_id=channel_id,
                days=days
            )

            if not stats:
                return {
                    "status": "no_data",
                    "message": f"No indexing history for channel {channel_id}",
                    "data": {}
                }

            return {
                "status": "success",
                "data": stats,
                "generated_at": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"[IndexHistoryAPI] Failed to get channel stats: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

    @staticmethod
    async def get_channel_jobs(channel_id: int, limit: int = 10, skip: int = 0):
        """Get recent jobs for a specific channel."""
        try:
            jobs = await IndexHistoryDB.get_job_history(
                limit=limit,
                skip=skip,
                channel_id=channel_id
            )

            # Convert datetime objects
            for job in jobs:
                if isinstance(job.get("finished"), datetime):
                    job["finished"] = job["finished"].isoformat()
                if isinstance(job.get("created_at"), datetime):
                    job["created_at"] = job["created_at"].isoformat()

            return {
                "status": "success",
                "channel_id": channel_id,
                "data": jobs,
                "count": len(jobs)
            }
        except Exception as e:
            logger.error(f"[IndexHistoryAPI] Failed to get channel jobs: {e}")
            return {
                "status": "error",
                "error": str(e),
                "data": []
            }

    @staticmethod
    async def get_summary():
        """Get quick summary of indexing activity."""
        try:
            total_jobs = await IndexHistoryDB.count_jobs(days=7)
            global_stats = await IndexHistoryDB.get_global_stats(days=7)

            return {
                "status": "success",
                "data": {
                    "jobs_last_7_days": total_jobs,
                    "total_indexed": global_stats.get("total_indexed", 0),
                    "total_duplicates": global_stats.get("total_duplicates", 0),
                    "total_errors": global_stats.get("total_errors", 0),
                    "avg_speed": global_stats.get("avg_speed", 0),
                    "success_rate": global_stats.get("success_rate", 0)
                },
                "generated_at": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"[IndexHistoryAPI] Failed to get summary: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
