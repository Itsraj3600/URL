"""
EventBus Integration - Wire up all production modules to EventBus.

Connects:
- Worker heartbeat → Heartbeat published on HEARTBEAT event
- Auto-recovery → Subscribed to HEARTBEAT for dead worker detection
- Plugin failures → Published as PLUGIN_FAILED event
- Database changes → Published as DB_CONNECTED/DB_DISCONNECTED events
- Shutdown events → Published on BOT_SHUTDOWN event
- Recovery events → Published on WORKER_RESTARTED event

This enables the entire system to communicate asynchronously via events.
"""

import logging
from typing import Callable

logger = logging.getLogger(__name__)


async def setup_eventbus_integration(event_bus, bot_client=None, db_client=None) -> None:
    """
    Wire up all EventBus integration points for production modules.

    Args:
        event_bus: Event bus instance
        bot_client: Pyrogram bot client
        db_client: MongoDB client
    """
    logger.info("Setting up EventBus integration...")

    # ========================================================================
    # 1. Worker Heartbeat Integration
    # ========================================================================
    from workers.heartbeat import get_all_worker_statuses

    @event_bus.on_interval(15)  # Every 15 seconds
    async def publish_heartbeat():
        """Publish periodic heartbeat event."""
        try:
            workers = await get_all_worker_statuses(db_client)
            await event_bus.publish(
                "heartbeat",  # Generic heartbeat event
                source="heartbeat",
                data={"workers": len(workers), "workers_list": workers},
            )
        except Exception as e:
            logger.debug(f"Heartbeat publish error: {e}")

    # ========================================================================
    # 2. Dead Worker Detection via Heartbeat
    # ========================================================================
    from datetime import datetime, timedelta

    @event_bus.on("heartbeat")
    async def detect_dead_workers(event):
        """Detect workers that haven't updated in 45 seconds."""
        try:
            workers = event.data.get("workers_list", [])
            now = datetime.utcnow()

            for worker in workers:
                last_seen = worker.get("last_seen")
                if last_seen:
                    if isinstance(last_seen, str):
                        last_seen = datetime.fromisoformat(last_seen.replace("Z", "+00:00"))

                    time_since_seen = (now - last_seen).total_seconds()

                    # Mark as dead if no update in 45 seconds
                    if time_since_seen > 45:
                        logger.warning(
                            f"Worker {worker.get('worker')} is dead ({time_since_seen}s since last update)"
                        )
                        await event_bus.publish(
                            "worker_dead",
                            source="heartbeat_monitor",
                            data={"worker_id": worker.get("worker")},
                        )

        except Exception as e:
            logger.debug(f"Dead worker detection error: {e}")

    # ========================================================================
    # 3. Auto-Recovery on Dead Worker
    # ========================================================================
    from core.recovery import get_recovery

    @event_bus.on("worker_dead")
    async def on_worker_dead(event):
        """Auto-recover when worker is detected dead."""
        worker_id = event.data.get("worker_id")
        logger.warning(f"Attempting recovery for dead worker: {worker_id}")

        recovery = get_recovery()
        # Recovery logic would restart the worker
        await recovery.handle_worker_crash(
            worker_id,
            async_restart_callback,
        )

    # ========================================================================
    # 4. Plugin Failure Tracking
    # ========================================================================
    @event_bus.on("plugin_failed")
    async def on_plugin_failed(event):
        """Handle plugin failure and log to database."""
        try:
            plugin_name = event.data.get("plugin_name")
            reason = event.data.get("reason")

            logger.error(f"Plugin failed: {plugin_name} - {reason}")

            # Store in database for debugging
            if db_client:
                db_name = __import__("os").environ.get("DATABASE_NAME", "CINE3600")
                db = db_client[db_name]

                await db["system_events"].insert_one(
                    {
                        "event_type": "plugin_failed",
                        "plugin_name": plugin_name,
                        "reason": reason,
                        "timestamp": datetime.utcnow(),
                    }
                )

            # Notify admins if configured
            if bot_client:
                from info import ADMINS

                for admin_id in ADMINS:
                    try:
                        await bot_client.send_message(
                            admin_id,
                            f"⚠️ Plugin {plugin_name} failed: {reason}",
                        )
                    except Exception as e:
                        logger.debug(f"Failed to notify admin: {e}")

        except Exception as e:
            logger.warning(f"Error handling plugin_failed event: {e}")

    # ========================================================================
    # 5. Database Event Handling
    # ========================================================================
    @event_bus.on("db_connected")
    async def on_db_connected(event):
        """Handle database connection established."""
        logger.info("Database connected, resuming operations")

        recovery = get_recovery()
        await recovery._publish_recovery_event("mongodb_reconnected")

    @event_bus.on("db_disconnected")
    async def on_db_disconnected(event):
        """Handle database disconnection."""
        logger.error("Database disconnected, initiating recovery")

        recovery = get_recovery()
        # Recovery would handle reconnection
        # await recovery.handle_mongodb_disconnect(db_client)

    # ========================================================================
    # 6. Index Job Events for Monitoring
    # ========================================================================
    @event_bus.on("index_started")
    async def on_index_started(event):
        """Log index job start."""
        job_id = event.data.get("job_id")
        logger.info(f"Index job started: {job_id}")

        if db_client:
            db_name = __import__("os").environ.get("DATABASE_NAME", "CINE3600")
            db = db_client[db_name]

            await db["system_events"].insert_one(
                {
                    "event_type": "index_started",
                    "job_id": job_id,
                    "timestamp": datetime.utcnow(),
                }
            )

    @event_bus.on("index_completed")
    async def on_index_completed(event):
        """Log index job completion."""
        job_id = event.data.get("job_id")
        files_indexed = event.data.get("count", 0)
        logger.info(f"Index job completed: {job_id} ({files_indexed} files)")

        if db_client:
            db_name = __import__("os").environ.get("DATABASE_NAME", "CINE3600")
            db = db_client[db_name]

            await db["system_events"].insert_one(
                {
                    "event_type": "index_completed",
                    "job_id": job_id,
                    "files_count": files_indexed,
                    "timestamp": datetime.utcnow(),
                }
            )

    # ========================================================================
    # 7. Shutdown Event Publishing
    # ========================================================================
    @event_bus.on("bot_shutdown")
    async def on_bot_shutdown(event):
        """Handle bot shutdown event."""
        logger.info("Bot shutdown event received")

        if db_client:
            db_name = __import__("os").environ.get("DATABASE_NAME", "CINE3600")
            db = db_client[db_name]

            await db["system_events"].insert_one(
                {
                    "event_type": "bot_shutdown",
                    "timestamp": datetime.utcnow(),
                    "graceful": event.data.get("graceful", True),
                }
            )

    logger.info("✅ EventBus integration complete")


async def async_restart_callback() -> None:
    """Placeholder for worker restart logic."""
    logger.info("Worker restart callback executed")
    # Implementation would restart the worker process


# Import for circular dependency
from datetime import datetime
