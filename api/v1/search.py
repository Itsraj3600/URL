"""
Search API Endpoints

GET /api/v1/search
    Perform a search.
    Params: q (query), limit, offset

GET /api/v1/search/suggestions
    Get search suggestions.
    Params: q (partial query)

GET /api/v1/search/popular
    Get popular queries.
    Params: limit

GET /api/v1/search/stats
    Get search statistics.
"""

from typing import Dict, Any, List


async def search(
    query: str,
    limit: int = 10,
    offset: int = 0,
    file_type: str = None
) -> Dict[str, Any]:
    """
    Perform a search.

    Args:
        query: Search query
        limit: Max results
        offset: Pagination offset
        file_type: Filter by type (video/audio/document)

    Returns:
        Search results
    """
    from core import get_container, get_event_bus, Events

    # Get search service
    container = get_container()
    search_service = container.get("search_service")

    # Perform search
    response = await search_service.search(
        query=query,
        max_results=limit,
        offset=offset,
        file_type=file_type
    )

    # Emit event
    bus = get_event_bus()
    await bus.publish(
        Events.SEARCH_PERFORMED,
        query=query,
        results_count=len(response.results),
        cache_hit=response.cache_hit,
        time_ms=response.search_time_ms
    )

    return {
        "query": response.query,
        "normalized": response.query_normalized,
        "results": [
            {
                "file_id": r.file_id,
                "file_name": r.file_name,
                "file_size": r.file_size,
                "file_type": r.file_type,
                "score": r.score,
            }
            for r in response.results
        ],
        "total": response.total,
        "offset": response.offset,
        "next_offset": response.next_offset,
        "cache_hit": response.cache_hit,
        "search_time_ms": response.search_time_ms,
    }


async def get_suggestions(query: str, limit: int = 5) -> List[str]:
    """Get search suggestions."""
    from core import get_container

    container = get_container()
    search_service = container.get("search_service")

    return await search_service.get_suggestions(query, limit=limit)


async def get_popular_queries(limit: int = 10) -> List[Dict[str, Any]]:
    """Get popular queries."""
    from core import get_container

    container = get_container()
    stats_service = container.get("stats_service")

    return stats_service.get_popular_queries(limit=limit)


async def get_search_stats(days: int = 7) -> Dict[str, Any]:
    """Get search statistics."""
    from api.dashboard import get_dashboard_api

    api = get_dashboard_api()
    return await api.get_search_analytics(days=days)


ENDPOINTS = {
    "GET /search": search,
    "GET /search/suggestions": get_suggestions,
    "GET /search/popular": get_popular_queries,
    "GET /search/stats": get_search_stats,
}
