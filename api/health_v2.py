"""
Health API v2 - Kubernetes-compatible health check endpoints.

Provides:
- GET /health - General health status
- GET /ready - Readiness probe (all systems ready?)
- GET /live - Liveness probe (process alive?)

Response includes detailed status of all components.
"""

import logging
import time
from datetime import datetime
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# Track startup time
_start_time = time.time()


class HealthChecker:
    """Health status checker for the bot."""

    def __init__(self):
        self.last_check = None
        self.check_interval = 5  # Cache health check for 5 seconds

    async def get_health_status(self) -> Dict[str, Any]:
        """
        Get comprehensive health status.

        Returns:
            Dict with status details
        """
        uptime_seconds = time.time() - _start_time

        return {
            "status": "healthy",
            "uptime": int(uptime_seconds),
            "timestamp": datetime.utcnow().isoformat(),
            "version": "2.0",
            "components": await self._get_components_status(),
        }

    async def get_readiness_status(self) -> Dict[str, Any]:
        """
        Get readiness status (Kubernetes readiness probe).

        Ready means all critical services are initialized and ready to accept traffic.

        Returns:
            Dict with readiness status
        """
        components = await self._get_components_status()

        # Check if all critical components are ready
        critical_ready = (
            components.get("mongodb", {}).get("status") == "online"
            and components.get("telegram", {}).get("status") == "connected"
            and components.get("workers", {}).get("count", 0) > 0
        )

        return {
            "ready": critical_ready,
            "status": "ready" if critical_ready else "not_ready",
            "timestamp": datetime.utcnow().isoformat(),
            "components": components,
        }

    async def get_liveness_status(self) -> Dict[str, Any]:
        """
        Get liveness status (Kubernetes liveness probe).

        Alive means the process is running and not in a deadlock.

        Returns:
            Dict with liveness status
        """
        uptime_seconds = time.time() - _start_time

        return {
            "alive": True,
            "status": "alive",
            "uptime": int(uptime_seconds),
            "timestamp": datetime.utcnow().isoformat(),
            "process": {
                "pid": __import__("os").getpid(),
                "memory_mb": self._get_memory_usage_mb(),
            },
        }

    async def _get_components_status(self) -> Dict[str, Any]:
        """Get status of all components."""
        return {
            "mongodb": await self._check_mongodb(),
            "telegram": await self._check_telegram(),
            "workers": await self._check_workers(),
            "queue": await self._check_queue(),
        }

    async def _check_mongodb(self) -> Dict[str, Any]:
        """Check MongoDB connection status."""
        try:
            from database.client import healthy_nodes

            nodes = healthy_nodes()

            return {
                "status": "online" if nodes else "offline",
                "nodes": len(nodes),
                "databases": [str(n) for n in nodes],
            }
        except Exception as e:
            logger.debug(f"MongoDB check failed: {e}")
            return {"status": "unknown", "error": str(e)}

    async def _check_telegram(self) -> Dict[str, Any]:
        """Check Telegram connection status."""
        try:
            from cinebot import Cine3600Bot

            if hasattr(Cine3600Bot, "get_me"):
                me = await Cine3600Bot.get_me()
                return {
                    "status": "connected",
                    "username": me.username,
                    "user_id": me.id,
                }
            else:
                return {"status": "not_initialized"}
        except Exception as e:
            logger.debug(f"Telegram check failed: {e}")
            return {"status": "disconnected", "error": str(e)}

    async def _check_workers(self) -> Dict[str, Any]:
        """Check worker status."""
        try:
            from workers.heartbeat import get_all_worker_statuses
            from database.client import PRIMARY

            workers = await get_all_worker_statuses(PRIMARY.client)

            return {
                "count": len(workers),
                "status": "healthy" if len(workers) > 0 else "no_workers",
                "workers": [
                    {
                        "id": w.get("worker"),
                        "status": w.get("status"),
                        "uptime": w.get("uptime"),
                    }
                    for w in workers
                ],
            }
        except Exception as e:
            logger.debug(f"Workers check failed: {e}")
            return {"count": 0, "status": "unknown", "error": str(e)}

    async def _check_queue(self) -> Dict[str, Any]:
        """Check job queue status."""
        try:
            from services import get_index_service

            service = get_index_service()
            if service:
                queue_size = getattr(service, "queue_size", 0)
                return {
                    "status": "healthy" if queue_size < 1000 else "high_load",
                    "size": queue_size,
                }
            return {"status": "not_initialized"}
        except Exception as e:
            logger.debug(f"Queue check failed: {e}")
            return {"status": "unknown", "error": str(e)}

    def _get_memory_usage_mb(self) -> float:
        """Get current process memory usage in MB."""
        try:
            import psutil
            import os

            process = psutil.Process(os.getpid())
            memory_info = process.memory_info()
            return round(memory_info.rss / (1024 * 1024), 2)
        except Exception:
            return 0.0


# Global health checker instance
_health_checker = HealthChecker()


def get_health_checker() -> HealthChecker:
    """Get global health checker instance."""
    return _health_checker
