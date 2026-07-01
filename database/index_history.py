"""
Index History Database

Stores and retrieves indexing job history.

Features:
- Persistent job records
- Statistics tracking
- Query history by date/channel
- Performance metrics
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

from database.client import get_primary

logger = logging.getLogger(__name__)


class IndexHistoryDB:
    """Manages index job history in MongoDB."""

    COLLECTION_NAME = "index_history"

    @classmethod
    def _collection(cls):
        primary = get_primary()
        if primary is None or primary.db is None:
            raise RuntimeError("Primary MongoDB database is not initialized")
        return primary.db[cls.COLLECTION_NAME]

    @classmethod
    async def initialize(cls):
        """Initialize the collection with proper indexes."""
        try:
            collection = cls._collection()

            await collection.create_index([("job_id", 1)], unique=True)
            await collection.create_index([("channel_id", 1)])
            await collection.create_index([("started_by", 1)])
            await collection.create_index([("finished", -1)])
            await collection.create_index([("type", 1)])
            await collection.create_index([("finished", 1)], expireAfterSeconds=63072000)

            logger.info("[IndexHistory] Initialized %s collection", cls.COLLECTION_NAME)
        except Exception as e:
            logger.error("[IndexHistory] Failed to initialize collection: %s", e)

    @classmethod
    async def save_job(
        cls,
        job_id: str,
        channel_id: int,
        channel_title: str,
        started_by: int,
        job_type: str,
        indexed: int,
        duplicates: int,
        skipped: int,
        errors: int,
        duration: int,
        average_speed: float,
        mongo_speed: float = 0.0,
        total_messages: int = 0,
        batch_size: int = 0,
        batches_completed: int = 0,
        largest_batch: int = 0,
        average_batch: float = 0.0,
        notes: str = "",
    ) -> bool:
        """Save a completed indexing job to history with enhanced metrics."""
        try:
            collection = cls._collection()
            total_processed = indexed + duplicates + skipped + errors
            record = {
                "job_id": job_id,
                "channel_id": channel_id,
                "channel_title": channel_title,
                "started_by": started_by,
                "type": job_type,
                "indexed": indexed,
                "duplicates": duplicates,
                "skipped": skipped,
                "errors": errors,
                "total_processed": total_processed,
                "success_rate": (indexed / total_processed * 100) if total_processed > 0 else 0,
                "duration": duration,
                "average_speed": average_speed,
                "mongo_speed": mongo_speed,
                "total_messages": total_messages,
                "batch_info": {
                    "batch_size": batch_size,
                    "batches_completed": batches_completed,
                    "largest_batch": largest_batch,
                    "average_batch": average_batch,
                },
                "notes": notes,
                "finished": datetime.utcnow(),
                "created_at": datetime.utcnow(),
            }

            result = await collection.insert_one(record)
            logger.info("[IndexHistory] Saved job %s - %s indexed", job_id, f"{indexed:,}")
            return bool(result.inserted_id)
        except Exception as e:
            logger.error("[IndexHistory] Failed to save job: %s", e)
            return False

    @classmethod
    async def get_job_history(
        cls,
        limit: int = 20,
        skip: int = 0,
        channel_id: Optional[int] = None,
        job_type: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Get recent job history with optional filters."""
        try:
            collection = cls._collection()
            query: Dict[str, Any] = {}

            if channel_id is not None:
                query["channel_id"] = channel_id
            if job_type:
                query["type"] = job_type

            cursor = collection.find(query).sort("finished", -1).skip(skip).limit(limit)
            return await cursor.to_list(length=limit)
        except Exception as e:
            logger.error("[IndexHistory] Failed to get job history: %s", e)
            return []

    @classmethod
    async def get_job(cls, job_id: str) -> Optional[Dict[str, Any]]:
        """Get details for a specific job."""
        try:
            collection = cls._collection()
            return await collection.find_one({"job_id": job_id})
        except Exception as e:
            logger.error("[IndexHistory] Failed to get job %s: %s", job_id, e)
            return None

    @classmethod
    async def get_stats_by_channel(cls, channel_id: int, days: int = 7) -> Dict[str, Any]:
        """Get aggregated statistics for a channel."""
        try:
            collection = cls._collection()
            cutoff_date = datetime.utcnow() - timedelta(days=days)

            pipeline = [
                {
                    "$match": {
                        "channel_id": channel_id,
                        "finished": {"$gte": cutoff_date},
                    }
                },
                {
                    "$group": {
                        "_id": "$channel_id",
                        "total_jobs": {"$sum": 1},
                        "total_indexed": {"$sum": "$indexed"},
                        "total_duplicates": {"$sum": "$duplicates"},
                        "total_errors": {"$sum": "$errors"},
                        "avg_speed": {"$avg": "$average_speed"},
                        "total_duration": {"$sum": "$duration"},
                    }
                },
            ]

            result = await collection.aggregate(pipeline).to_list(length=1)

            if not result:
                return {}

            stats = result[0]
            return {
                "channel_id": channel_id,
                "period_days": days,
                "jobs": stats.get("total_jobs", 0),
                "indexed": stats.get("total_indexed", 0),
                "duplicates": stats.get("total_duplicates", 0),
                "errors": stats.get("total_errors", 0),
                "avg_speed": stats.get("avg_speed", 0),
                "total_duration": stats.get("total_duration", 0),
            }
        except Exception as e:
            logger.error("[IndexHistory] Failed to get channel stats: %s", e)
            return {}

    @classmethod
    async def get_global_stats(cls, days: int = 30) -> Dict[str, Any]:
        """Get global indexing statistics."""
        try:
            collection = cls._collection()
            cutoff_date = datetime.utcnow() - timedelta(days=days)

            pipeline = [
                {"$match": {"finished": {"$gte": cutoff_date}}},
                {
                    "$group": {
                        "_id": None,
                        "total_jobs": {"$sum": 1},
                        "total_indexed": {"$sum": "$indexed"},
                        "total_duplicates": {"$sum": "$duplicates"},
                        "total_errors": {"$sum": "$errors"},
                        "avg_speed": {"$avg": "$average_speed"},
                        "max_speed": {"$max": "$average_speed"},
                        "total_duration": {"$sum": "$duration"},
                    }
                },
            ]

            result = await collection.aggregate(pipeline).to_list(length=1)

            if not result:
                return {}

            stats = result[0]
            total_processed = stats.get("total_indexed", 0) + stats.get("total_duplicates", 0)
            return {
                "period_days": days,
                "total_jobs": stats.get("total_jobs", 0),
                "total_indexed": stats.get("total_indexed", 0),
                "total_duplicates": stats.get("total_duplicates", 0),
                "total_errors": stats.get("total_errors", 0),
                "total_processed": total_processed,
                "success_rate": (stats.get("total_indexed", 0) / total_processed * 100)
                if total_processed > 0
                else 0,
                "avg_speed": stats.get("avg_speed", 0),
                "max_speed": stats.get("max_speed", 0),
                "total_duration": stats.get("total_duration", 0),
            }
        except Exception as e:
            logger.error("[IndexHistory] Failed to get global stats: %s", e)
            return {}

    @classmethod
    async def count_jobs(cls, days: int = 7) -> int:
        """Count jobs in the last N days."""
        try:
            collection = cls._collection()
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            return await collection.count_documents({"finished": {"$gte": cutoff_date}})
        except Exception as e:
            logger.error("[IndexHistory] Failed to count jobs: %s", e)
            return 0

    @classmethod
    async def delete_old_records(cls, days: int = 730) -> int:
        """Delete records older than N days."""
        try:
            collection = cls._collection()
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            result = await collection.delete_many({"finished": {"$lt": cutoff_date}})
            logger.info("[IndexHistory] Deleted %s old records", result.deleted_count)
            return result.deleted_count
        except Exception as e:
            logger.error("[IndexHistory] Failed to delete old records: %s", e)
            return 0
