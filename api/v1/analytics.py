"""
Analytics API Endpoints

GET /api/v1/analytics/search
    Get search analytics.
    Params: days (default 7)

GET /api/v1/analytics/index
    Get index analytics.

GET /api/v1/analytics/users
    Get user analytics.

GET /api/v1/analytics/overview
    Get overall analytics summary.
"""

from typing import Dict, Any


async def get_search_analytics(days: int = 7) -> Dict[str, Any]:
    """Get search analytics."""
    from api.dashboard import get_dashboard_api

    api = get_dashboard_api()
    return await api.get_search_analytics(days=days)


async def get_index_analytics() -> Dict[str, Any]:
    """Get index analytics."""
    from api.dashboard import get_dashboard_api

    api = get_dashboard_api()
    return await api.get_index_analytics()


async def get_analytics_overview() -> Dict[str, Any]:
    """Get overall analytics summary."""
    from api.dashboard import get_dashboard_api

    api = get_dashboard_api()

    search = await api.get_search_analytics(days=7)
    index = await api.get_index_analytics()

    return {
        "search": {
            "total_searches": search.get("performance", {}).get("total_searches", 0),
            "avg_time_ms": search.get("performance", {}).get("avg_search_time_ms", 0),
            "cache_hit_rate": search.get("performance", {}).get("cache_hit_rate", 0),
            "popular_queries": search.get("popular_queries", [])[:5],
        },
        "index": {
            "total_jobs": index.get("aggregate", {}).get("total_jobs", 0),
            "total_files": index.get("aggregate", {}).get("total_files_indexed", 0),
            "avg_speed": index.get("aggregate", {}).get("avg_speed", 0),
        },
    }


ENDPOINTS = {
    "GET /analytics/search": get_search_analytics,
    "GET /analytics/index": get_index_analytics,
    "GET /analytics/overview": get_analytics_overview,
}
