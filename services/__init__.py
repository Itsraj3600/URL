"""
Services Layer for CINE3600

This package provides service-based architecture for:
- Search operations (SearchService)
- Caching (CacheService)
- Pagination (PaginationService)
- Statistics (StatsService)
- And more...

Usage:
    from services import get_search_service, get_stats_service

    search = get_search_service()
    results = await search.search("avatar")

    stats = get_stats_service()
    stats.record_search(query="avatar", results_count=10, ...)
"""

# Search Service
from services.search_service import (
    SearchService,
    SearchResult,
    SearchResponse,
    SearchStats,
    ProfileResult,
    get_search_service,
    reset_search_service,
)

# Cache Service
from services.cache_service import (
    CacheService,
    MemoryCache,
    CacheEntry,
    CacheStats,
    get_cache_service,
    reset_cache_service,
)

# Pagination Service
from services.pagination_service import (
    PaginationService,
    PageResult,
    PaginationState,
    get_pagination_service,
    reset_pagination_service,
)

# Stats Service
from services.stats_service import (
    StatsService,
    SearchMetric,
    QueryStat,
    UserStat,
    HourlyStats,
    get_stats_service,
    reset_stats_service,
)

__all__ = [
    # Search
    "SearchService",
    "SearchResult",
    "SearchResponse",
    "SearchStats",
    "ProfileResult",
    "get_search_service",
    "reset_search_service",
    # Cache
    "CacheService",
    "MemoryCache",
    "CacheEntry",
    "CacheStats",
    "get_cache_service",
    "reset_cache_service",
    # Pagination
    "PaginationService",
    "PageResult",
    "PaginationState",
    "get_pagination_service",
    "reset_pagination_service",
    # Stats
    "StatsService",
    "SearchMetric",
    "QueryStat",
    "UserStat",
    "HourlyStats",
    "get_stats_service",
    "reset_stats_service",
]
