"""
Database Schema Initialization - Create collections and indexes for production features.

Sets up 4 new MongoDB collections for:
- worker_status: Real-time worker heartbeat data
- worker_metrics: Historical worker performance metrics
- system_events: Audit trail of system events
- health_checks: Health check history

Also creates indexes for efficient querying.
"""

import logging
from datetime import datetime

logger = logging.getLogger(__name__)


async def setup_production_schema(db_client) -> bool:
    """
    Create production schema and indexes.

    Args:
        db_client: Motor MongoDB client

    Returns:
        True if successful, False otherwise
    """
    try:
        db_name = __import__("os").environ.get("DATABASE_NAME", "CINE3600")
        db = db_client[db_name]

        # Create worker_status collection
        await _create_worker_status_collection(db)

        # Create worker_metrics collection
        await _create_worker_metrics_collection(db)

        # Create system_events collection
        await _create_system_events_collection(db)

        # Create health_checks collection
        await _create_health_checks_collection(db)

        logger.info("✅ Production schema initialized")
        return True

    except Exception as e:
        logger.error(f"Failed to setup production schema: {e}", exc_info=True)
        return False


async def _create_worker_status_collection(db) -> None:
    """Create worker_status collection with indexes."""
    collection = db["worker_status"]

    # Create text index for worker field
    try:
        await collection.create_index("worker", unique=True)
        logger.debug("Created index on worker_status.worker")
    except Exception as e:
        logger.debug(f"Index already exists: {e}")

    # Create index for last_seen (for finding stale workers)
    try:
        await collection.create_index("last_seen")
        logger.debug("Created index on worker_status.last_seen")
    except Exception:
        pass

    # Insert sample if empty
    count = await collection.count_documents({})
    if count == 0:
        await collection.insert_one(
            {
                "worker": "main",
                "status": "starting",
                "uptime": 0,
                "version": "2.0",
                "last_seen": datetime.utcnow(),
                "current_job": "initializing",
                "memory_mb": 0,
                "cpu_percent": 0,
                "tasks_completed": 0,
                "errors": 0,
            }
        )

    logger.info("✅ worker_status collection ready")


async def _create_worker_metrics_collection(db) -> None:
    """Create worker_metrics collection with indexes."""
    collection = db["worker_metrics"]

    # Create index on worker and timestamp
    try:
        await collection.create_index([("worker", 1), ("timestamp", -1)])
        logger.debug("Created index on worker_metrics")
    except Exception:
        pass

    # Create TTL index to auto-expire metrics after 30 days
    try:
        await collection.create_index(
            "timestamp",
            expireAfterSeconds=30 * 24 * 60 * 60,  # 30 days
        )
        logger.debug("Created TTL index on worker_metrics")
    except Exception:
        pass

    logger.info("✅ worker_metrics collection ready")


async def _create_system_events_collection(db) -> None:
    """Create system_events collection with indexes."""
    collection = db["system_events"]

    # Create index on event_type and timestamp
    try:
        await collection.create_index([("event_type", 1), ("timestamp", -1)])
        logger.debug("Created index on system_events")
    except Exception:
        pass

    # Create TTL index to auto-expire events after 90 days
    try:
        await collection.create_index(
            "timestamp",
            expireAfterSeconds=90 * 24 * 60 * 60,  # 90 days
        )
        logger.debug("Created TTL index on system_events")
    except Exception:
        pass

    logger.info("✅ system_events collection ready")


async def _create_health_checks_collection(db) -> None:
    """Create health_checks collection with indexes."""
    collection = db["health_checks"]

    # Create index on timestamp
    try:
        await collection.create_index("timestamp")
        logger.debug("Created index on health_checks")
    except Exception:
        pass

    # Create TTL index to auto-expire old checks after 14 days
    try:
        await collection.create_index(
            "timestamp",
            expireAfterSeconds=14 * 24 * 60 * 60,  # 14 days
        )
        logger.debug("Created TTL index on health_checks")
    except Exception:
        pass

    logger.info("✅ health_checks collection ready")
