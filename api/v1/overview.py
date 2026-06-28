"""
Overview API Endpoint

GET /api/v1/overview
    Returns dashboard overview statistics.

Response:
{
    "bot_status": "online",
    "users": 18432,
    "files": 492318,
    "channels": 27,
    "searches_today": 52117,
    "downloads_today": 13921,
    "cache_hit_rate": 93.2,
    "indexing_status": "running",
    "health": {
        "database": "healthy",
        "workers": "8/8 active",
        "cache": "93%"
    }
}
"""

from typing import Dict, Any
from datetime import datetime


async def get_overview() -> Dict[str, Any]:
    """
    Get dashboard overview statistics.

    Returns:
        Overview data dict
    """
    from api.dashboard import get_dashboard_api

    api = get_dashboard_api()
    stats = await api.get_overview()

    return {
        "bot_status": stats.bot_status,
        "uptime_seconds": stats.uptime_seconds,
        "users": stats.total_users,
        "files": stats.total_files,
        "channels": stats.total_channels,
        "searches_today": stats.searches_today,
        "downloads_today": stats.downloads_today,
        "cache_hit_rate": stats.cache_hit_rate,
        "avg_search_time_ms": stats.avg_search_time_ms,
        "indexing": {
            "status": stats.indexing_status,
            "progress": stats.indexing_progress,
        },
        "health": {
            "database": stats.db_status,
            "workers": f"{stats.active_workers}/{stats.total_workers}",
            "cache": f"{stats.cache_hit_rate:.1f}%",
        },
        "timestamp": datetime.utcnow().isoformat(),
    }


# Export for router
ENDPOINTS = {
    "GET /overview": get_overview,
}
