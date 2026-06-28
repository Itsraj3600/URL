"""
Health API Endpoints

GET /api/v1/health
    Get system health status.

GET /api/v1/health/live
    Liveness probe.

GET /api/v1/health/ready
    Readiness probe.
"""

from typing import Dict, Any
from datetime import datetime


async def get_health() -> Dict[str, Any]:
    """Get comprehensive health status."""
    from api.dashboard import get_dashboard_api

    api = get_dashboard_api()
    return await api.get_health()


async def liveness() -> Dict[str, Any]:
    """Liveness probe - is the service running?"""
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat(),
    }


async def readiness() -> Dict[str, Any]:
    """Readiness probe - is the service ready to serve?"""
    from database.client import healthy_nodes

    try:
        nodes = healthy_nodes()
        if nodes:
            return {
                "status": "ready",
                "database": "connected",
                "timestamp": datetime.utcnow().isoformat(),
            }
        return {
            "status": "not_ready",
            "database": "disconnected",
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        return {
            "status": "not_ready",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat(),
        }


ENDPOINTS = {
    "GET /health": get_health,
    "GET /health/live": liveness,
    "GET /health/ready": readiness,
}
