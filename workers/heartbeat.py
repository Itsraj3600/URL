"""
Worker Heartbeat - Real-time worker health monitoring.

Each worker (main, index, cleanup, stats) updates MongoDB every 15 seconds
with its current status, resource usage, and job information.

This enables:
- Real-time worker status on dashboard
- Dead worker detection
- Auto-recovery triggering
- Performance monitoring
"""

import logging
import asyncio
import psutil
import os
from datetime import datetime
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class WorkerHeartbeat:
    """Manages worker heartbeat updates to MongoDB."""

    def __init__(self, worker_id: str, db_client):
        """
        Initialize worker heartbeat.

        Args:
            worker_id: Unique worker identifier (e.g., "main", "index_1")
            db_client: Motor MongoDB client
        """
        self.worker_id = worker_id
        self.db_client = db_client
        self.collection = None
        self.running = False
        self.current_job = None
        self.tasks_completed = 0
        self.errors_count = 0
        self.start_time = datetime.utcnow()

        # Initialize collection
        if db_client:
            db_name = os.environ.get("DATABASE_NAME", "CINE3600")
            self.collection = db_client[db_name]["worker_status"]

    async def start(self) -> None:
        """Start periodic heartbeat updates."""
        self.running = True
        logger.info(f"Starting heartbeat for worker: {self.worker_id}")

        try:
            while self.running:
                await self._send_heartbeat()
                await asyncio.sleep(15)  # Update every 15 seconds
        except asyncio.CancelledError:
            await self.stop()
        except Exception as e:
            logger.error(f"Heartbeat error: {e}", exc_info=True)

    async def stop(self) -> None:
        """Stop heartbeat and mark worker as offline."""
        self.running = False
        logger.info(f"Stopping heartbeat for worker: {self.worker_id}")

        if self.collection:
            try:
                await self.collection.update_one(
                    {"worker": self.worker_id},
                    {
                        "$set": {
                            "status": "offline",
                            "last_seen": datetime.utcnow(),
                        }
                    },
                )
            except Exception as e:
                logger.warning(f"Failed to mark worker offline: {e}")

    async def set_job(self, job_name: str) -> None:
        """Update current job being processed."""
        self.current_job = job_name
        await self._send_heartbeat()

    async def increment_completed(self) -> None:
        """Increment tasks completed counter."""
        self.tasks_completed += 1

    async def increment_errors(self) -> None:
        """Increment error counter."""
        self.errors_count += 1

    async def _send_heartbeat(self) -> None:
        """Send heartbeat to MongoDB."""
        if not self.collection:
            return

        try:
            # Collect system metrics
            process = psutil.Process(os.getpid())
            memory_info = process.memory_info()
            memory_mb = memory_info.rss / (1024 * 1024)

            try:
                cpu_percent = process.cpu_percent(interval=0.1)
            except Exception:
                cpu_percent = 0.0

            # Calculate uptime
            uptime_seconds = (datetime.utcnow() - self.start_time).total_seconds()

            # Build heartbeat document
            heartbeat_data = {
                "worker": self.worker_id,
                "status": "online" if self.running else "offline",
                "uptime": int(uptime_seconds),
                "version": "2.0",
                "last_seen": datetime.utcnow(),
                "current_job": self.current_job or "idle",
                "memory_mb": round(memory_mb, 2),
                "cpu_percent": round(cpu_percent, 1),
                "tasks_completed": self.tasks_completed,
                "errors": self.errors_count,
            }

            # Upsert to MongoDB
            await self.collection.update_one(
                {"worker": self.worker_id},
                {"$set": heartbeat_data},
                upsert=True,
            )

            logger.debug(f"Heartbeat sent: {self.worker_id} - {heartbeat_data}")

        except Exception as e:
            logger.warning(f"Failed to send heartbeat: {e}")

    async def get_status(self) -> Optional[Dict[str, Any]]:
        """Get current worker status from MongoDB."""
        if not self.collection:
            return None

        try:
            return await self.collection.find_one({"worker": self.worker_id})
        except Exception as e:
            logger.warning(f"Failed to get worker status: {e}")
            return None


async def get_all_worker_statuses(db_client) -> list:
    """Get status of all workers from MongoDB."""
    try:
        db_name = os.environ.get("DATABASE_NAME", "CINE3600")
        collection = db_client[db_name]["worker_status"]

        # Get all online workers
        workers = await collection.find({"status": "online"}).to_list(None)
        return workers

    except Exception as e:
        logger.warning(f"Failed to get worker statuses: {e}")
        return []


async def get_worker_status(db_client, worker_id: str) -> Optional[Dict[str, Any]]:
    """Get status of specific worker."""
    try:
        db_name = os.environ.get("DATABASE_NAME", "CINE3600")
        collection = db_client[db_name]["worker_status"]
        return await collection.find_one({"worker": worker_id})
    except Exception as e:
        logger.warning(f"Failed to get worker status: {e}")
        return None
