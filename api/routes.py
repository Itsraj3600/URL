"""
API Routes for Dashboard

FastAPI-style route definitions that can be used with the Next.js API.
"""

from datetime import datetime
from typing import Optional
import logging

logger = logging.getLogger(__name__)


# Route definitions
ROUTES = {
    # Overview
    "GET /api/overview": {
        "handler": "get_overview",
        "description": "Get dashboard overview statistics"
    },
    # Users
    "GET /api/users": {
        "handler": "get_users",
        "description": "List users with optional filters"
    },
    "GET /api/users/:id": {
        "handler": "get_user",
        "description": "Get single user details"
    },
    "POST /api/users/:id/ban": {
        "handler": "ban_user",
        "description": "Ban a user"
    },
    "POST /api/users/:id/unban": {
        "handler": "unban_user",
        "description": "Unban a user"
    },
    # Indexing
    "GET /api/index/jobs": {
        "handler": "get_index_jobs",
        "description": "List all index jobs"
    },
    "GET /api/index/jobs/:id": {
        "handler": "get_index_job",
        "description": "Get single job details"
    },
    "POST /api/index/start": {
        "handler": "start_index",
        "description": "Start new index job"
    },
    "POST /api/index/:id/pause": {
        "handler": "pause_index",
        "description": "Pause index job"
    },
    "POST /api/index/:id/resume": {
        "handler": "resume_index",
        "description": "Resume index job"
    },
    "POST /api/index/:id/cancel": {
        "handler": "cancel_index",
        "description": "Cancel index job"
    },
    # Channels
    "GET /api/channels": {
        "handler": "get_channels",
        "description": "List connected channels"
    },
    # Logs
    "GET /api/logs": {
        "handler": "get_logs",
        "description": "Get recent logs"
    },
    # Health
    "GET /api/health": {
        "handler": "get_health",
        "description": "Get system health status"
    },
    # Analytics
    "GET /api/analytics/search": {
        "handler": "get_search_analytics",
        "description": "Get search analytics data"
    },
    "GET /api/analytics/index": {
        "handler": "get_index_analytics",
        "description": "Get index analytics data"
    },
    # Cache
    "GET /api/cache/stats": {
        "handler": "get_cache_stats",
        "description": "Get cache statistics"
    },
    "POST /api/cache/clear": {
        "handler": "clear_cache",
        "description": "Clear cache(s)"
    },
}


async def handle_request(method: str, path: str, params: dict = None, body: dict = None):
    """
    Handle an API request.

    Args:
        method: HTTP method (GET, POST, etc.)
        path: Request path
        params: Query parameters
        body: Request body

    Returns:
        Response data dict
    """
    from api.dashboard import get_dashboard_api

    api = get_dashboard_api()
    params = params or {}
    body = body or {}

    # Route handlers
    if method == "GET" and path == "/api/overview":
        return await api.get_overview()

    elif method == "GET" and path == "/api/users":
        return await api.get_users(
            limit=params.get("limit", 50),
            offset=params.get("offset", 0),
            search=params.get("search", ""),
            banned_only=params.get("banned_only", False),
            premium_only=params.get("premium_only", False)
        )

    elif method == "GET" and path.startswith("/api/users/"):
        user_id = int(path.split("/")[-1])
        return await api.get_user(user_id)

    elif method == "POST" and path.startswith("/api/users/") and path.endswith("/ban"):
        user_id = int(path.split("/")[-2])
        return await api.ban_user(user_id, body.get("reason", ""))

    elif method == "POST" and path.startswith("/api/users/") and path.endswith("/unban"):
        user_id = int(path.split("/")[-2])
        return await api.unban_user(user_id)

    elif method == "GET" and path == "/api/index/jobs":
        return await api.get_index_jobs()

    elif method == "POST" and path == "/api/index/start":
        return await api.start_index(
            channel_id=body.get("channel_id"),
            last_message_id=body.get("last_message_id"),
            requested_by=body.get("requested_by", 0)
        )

    elif method == "POST" and path.startswith("/api/index/") and path.endswith("/pause"):
        job_id = path.split("/")[-2]
        return await api.pause_index(job_id)

    elif method == "POST" and path.startswith("/api/index/") and path.endswith("/resume"):
        job_id = path.split("/")[-2]
        return await api.resume_index(job_id)

    elif method == "POST" and path.startswith("/api/index/") and path.endswith("/cancel"):
        job_id = path.split("/")[-2]
        return await api.cancel_index(job_id)

    elif method == "GET" and path == "/api/channels":
        return await api.get_channels()

    elif method == "GET" and path == "/api/logs":
        return await api.get_logs(
            limit=params.get("limit", 100),
            level=params.get("level", ""),
            search=params.get("search", "")
        )

    elif method == "GET" and path == "/api/health":
        return await api.get_health()

    elif method == "GET" and path == "/api/analytics/search":
        return await api.get_search_analytics(days=params.get("days", 7))

    elif method == "GET" and path == "/api/analytics/index":
        return await api.get_index_analytics()

    elif method == "GET" and path == "/api/cache/stats":
        return await api.get_cache_stats()

    elif method == "POST" and path == "/api/cache/clear":
        return await api.clear_cache(cache_type=body.get("type", "all"))

    else:
        return {"error": "Not found", "status": 404}
