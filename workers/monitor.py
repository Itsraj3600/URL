"""
Worker Monitor - Real-time worker metrics and performance monitoring.

Collects metrics from each worker and stores in MongoDB for:
- Performance analysis
- Alerts on slow/failing workers
- Historical trend analysis
- Dashboard display

Provides `/api/workers` endpoint with real-time status.
"""

import logging
import asyncio
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class WorkerMonitor:
    """Monitors worker performance and health."""

    def __init__(self, db_client):
        """
        Initialize worker monitor.

        Args:
            db_client: Motor MongoDB client
        """
        self.db_client = db_client
        self.collection = None
        self.running = False

        if db_client:
            db_name = os.environ.get("DATABASE_NAME", "CINE3600")
            self.collection = db_client[db_name]["worker_metrics"]

    async def start(self) -> None:
        """Start monitoring workers."""
        self.running = True
        logger.info("Worker monitor started")

        try:
            while self.running:
                await self._collect_metrics()
                await asyncio.sleep(60)  # Collect every 60 seconds
        except asyncio.CancelledError:
            self.running = False
        except Exception as e:
            logger.error(f"Monitor error: {e}", exc_info=True)

    async def stop(self) -> None:
        """Stop monitoring workers."""
        self.running = False
        logger.info("Worker monitor stopped")

    async def _collect_metrics(self) -> None:
        """Collect metrics from all workers."""
        try:
            from workers.heartbeat import get_all_worker_statuses

            workers = await get_all_worker_statuses(self.db_client)

            for worker in workers:
                await self._store_worker_metrics(worker)

        except Exception as e:
            logger.warning(f"Failed to collect metrics: {e}")

    async def _store_worker_metrics(self, worker_data: Dict[str, Any]) -> None:
        """Store worker metrics snapshot to database."""
        if not self.collection:
            return

        try:
            metrics_record = {
                "worker": worker_data.get("worker"),
                "timestamp": datetime.utcnow(),
                "status": worker_data.get("status"),
                "uptime": worker_data.get("uptime"),
                "memory_mb": worker_data.get("memory_mb"),
                "cpu_percent": worker_data.get("cpu_percent"),
                "tasks_completed": worker_data.get("tasks_completed"),
                "errors": worker_data.get("errors"),
            }

            await self.collection.insert_one(metrics_record)

        except Exception as e:
            logger.warning(f"Failed to store metrics: {e}")

    async def get_worker_metrics(
        self, worker_id: str, hours: int = 24
    ) -> List[Dict[str, Any]]:
        """
        Get historical metrics for a worker.

        Args:
            worker_id: Worker ID
            hours: Number of hours of history to retrieve

        Returns:
            List of metrics records
        """
        if not self.collection:
            return []

        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)

            metrics = await self.collection.find(
                {
                    "worker": worker_id,
                    "timestamp": {"$gte": cutoff_time},
                }
            ).to_list(None)

            return sorted(metrics, key=lambda x: x["timestamp"])

        except Exception as e:
            logger.warning(f"Failed to get metrics: {e}")
            return []

    async def get_worker_stats(self, worker_id: str, hours: int = 24) -> Optional[Dict[str, Any]]:
        """
        Calculate statistics for a worker over a time period.

        Args:
            worker_id: Worker ID
            hours: Number of hours to analyze

        Returns:
            Dict with statistics or None
        """
        metrics = await self.get_worker_metrics(worker_id, hours)

        if not metrics:
            return None

        try:
            memory_values = [m.get("memory_mb", 0) for m in metrics]
            cpu_values = [m.get("cpu_percent", 0) for m in metrics]

            return {
                "worker": worker_id,
                "period_hours": hours,
                "metrics_count": len(metrics),
                "memory": {
                    "min": min(memory_values),
                    "max": max(memory_values),
                    "avg": sum(memory_values) / len(memory_values),
                },
                "cpu": {
                    "min": min(cpu_values),
                    "max": max(cpu_values),
                    "avg": sum(cpu_values) / len(cpu_values),
                },
                "tasks_completed": metrics[-1].get("tasks_completed", 0),
                "errors": metrics[-1].get("errors", 0),
            }
        except Exception as e:
            logger.warning(f"Failed to calculate stats: {e}")
            return None

    async def check_alerts(self) -> List[Dict[str, Any]]:
        """
        Check for alert conditions across all workers.

        Returns:
            List of alerts
        """
        alerts = []

        try:
            from workers.heartbeat import get_all_worker_statuses

            workers = await get_all_worker_statuses(self.db_client)

            for worker in workers:
                # Check high memory usage (>500MB)
                memory = worker.get("memory_mb", 0)
                if memory > 500:
                    alerts.append(
                        {
                            "type": "high_memory",
                            "worker": worker.get("worker"),
                            "value": memory,
                            "message": f"Worker memory usage high: {memory}MB",
                        }
                    )

                # Check high CPU usage (>80%)
                cpu = worker.get("cpu_percent", 0)
                if cpu > 80:
                    alerts.append(
                        {
                            "type": "high_cpu",
                            "worker": worker.get("worker"),
                            "value": cpu,
                            "message": f"Worker CPU usage high: {cpu}%",
                        }
                    )

                # Check error rate (errors > tasks/10)
                errors = worker.get("errors", 0)
                tasks = worker.get("tasks_completed", 1)
                error_rate = errors / tasks if tasks > 0 else 0

                if error_rate > 0.1:  # More than 10% error rate
                    alerts.append(
                        {
                            "type": "high_error_rate",
                            "worker": worker.get("worker"),
                            "value": error_rate,
                            "message": f"Worker error rate high: {error_rate*100:.1f}%",
                        }
                    )

        except Exception as e:
            logger.warning(f"Failed to check alerts: {e}")

        return alerts


# Global monitor instance
_monitor = None


def get_worker_monitor() -> Optional[WorkerMonitor]:
    """Get global worker monitor instance."""
    return _monitor


async def init_worker_monitor(db_client) -> None:
    """Initialize global worker monitor."""
    global _monitor
    _monitor = WorkerMonitor(db_client)
    asyncio.create_task(_monitor.start())
