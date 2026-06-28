"""
Services Layer for CINE3600

This package provides service-based architecture for:
- Search operations (SearchService)
- Caching (CacheService)
- Pagination (PaginationService)
- Statistics (StatsService)
- Indexing (IndexService)
- Progress tracking (ProgressService)
- Index statistics (IndexStatsService)
- And more...

Usage:
    from services import get_search_service, get_index_service

    search = get_search_service()
    results = await search.search("avatar")

    index = get_index_service()
    job = await index.start_job(channel_id=-100..., last_message_id=50000)
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

# Stats Service (Search Stats)
from services.stats_service import (
    StatsService,
    SearchMetric,
    QueryStat,
    UserStat,
    HourlyStats,
    get_stats_service,
    reset_stats_service,
)

# Index Service
from services.index_service import (
    IndexService,
    IndexJob,
    DuplicateInfo,
    DuplicateReason,
    MediaMetadata,
    IndexStats,
    JobStatus,
    get_index_service,
    reset_index_service,
)

# Progress Service
from services.progress_service import (
    ProgressService,
    ProgressState,
    ProgressStage,
    get_progress_service,
    reset_progress_service,
)

# Index Stats Service
from services.index_stats_service import (
    IndexStatsService,
    JobStatistics,
    AggregateStats,
    DailyStats,
    get_index_stats_service,
    reset_index_stats_service,
)

# Shared State Service
from services.shared_state import (
    SharedStateService,
    BotStatus,
    IndexStatus,
    WorkerStatus,
    StateKeys,
    get_shared_state,
    initialize_shared_state,
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
    # Index
    "IndexService",
    "IndexJob",
    "DuplicateInfo",
    "DuplicateReason",
    "MediaMetadata",
    "IndexStats",
    "JobStatus",
    "get_index_service",
    "reset_index_service",
    # Progress
    "ProgressService",
    "ProgressState",
    "ProgressStage",
    "get_progress_service",
    "reset_progress_service",
    # Index Stats
    "IndexStatsService",
    "JobStatistics",
    "AggregateStats",
    "DailyStats",
    "get_index_stats_service",
    "reset_index_stats_service",
    # Shared State
    "SharedStateService",
    "BotStatus",
    "IndexStatus",
    "WorkerStatus",
    "StateKeys",
    "get_shared_state",
    "initialize_shared_state",
]
