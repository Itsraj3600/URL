"""
Search Service v2

A unified search service that handles:
- Query normalization
- Search ranking/scoring
- Multi-layer caching
- Pagination caching
- Search statistics
- Search suggestions
- Performance profiling

This service becomes the single entry point for all search operations.
"""

import logging
import re
import time
import asyncio
from collections import OrderedDict
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional, Tuple, Any
from functools import wraps

logger = logging.getLogger(__name__)


# =============================================================================
# Configuration
# =============================================================================

SEARCH_CACHE_TTL_SECONDS = int(__import__('os').environ.get("SEARCH_CACHE_TTL_SECONDS", 600))
SEARCH_CACHE_MAX_ENTRIES = int(__import__('os').environ.get("SEARCH_CACHE_MAX_ENTRIES", 1000))
PAGINATION_CACHE_TTL_SECONDS = int(__import__('os').environ.get("PAGINATION_CACHE_TTL_SECONDS", 900))
SUGGESTION_LIMIT = int(__import__('os').environ.get("SUGGESTION_LIMIT", 5))


# =============================================================================
# Release Tag Patterns for Normalization
# =============================================================================

RELEASE_TAG_PATTERNS = [
    # Quality tags
    r"\b480p\b", r"\b720p\b", r"\b1080p\b", r"\b2160p\b", r"\b4k\b",
    # Codec tags
    r"\bx264\b", r"\bx265\b", r"\bhevc\b", r"\bavc\b", r"\bav1\b",
    # Source tags
    r"\bhdrip\b", r"\bbrrip\b", r"\bbluray\b", r"\bweb[- ]?dl\b",
    r"\bweb[- ]?rip\b", r"\bhdtv\b", r"\bdvdrip\b", r"\bcamrip\b",
    r"\bwebdl\b", r"\bwebrip\b",
    # Audio tags
    r"\baac\b", r"\bddp\d+\.?\d*\b", r"\bac3\b", r"\bdts\b",
    r"\btruehd\b", r"\batmos\b",
    # Other tags
    r"\b10bit\b", r"\b8bit\b", r"\bmulti\b", r"\bproper\b",
    r"\bremux\b", r"\bhdr\b", r"\bdv\b", r"\bdolby\s*vision\b",
    # Release groups (common patterns)
    r"\b[tT][eE][aA][mM]\b", r"\b[rR][gG]\b",
]

RELEASE_TAG_RE = re.compile("|".join(RELEASE_TAG_PATTERNS), re.IGNORECASE)

BRACKET_TAG_RE = re.compile(r"[\[\(\{].*?[\]\)\}]")
NON_WORD_RE = re.compile(r"[^\w\s]+")
YEAR_RE = re.compile(r"\b(19\d{2}|20\d{2})\b")
MULTI_SPACE_RE = re.compile(r"\s+")


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class SearchResult:
    """Represents a single search result with scoring."""
    file_id: str
    file_name: str
    file_name_normalized: str
    file_size: int
    file_type: str
    caption: Optional[str] = None
    file_ref: Optional[str] = None
    score: int = 0
    match_type: str = "none"


@dataclass
class SearchResponse:
    """Complete search response with metadata."""
    results: List[SearchResult]
    total: int
    query: str
    query_normalized: str
    offset: int
    next_offset: str
    cache_hit: bool
    search_time_ms: float
    mongo_time_ms: float = 0.0
    rank_time_ms: float = 0.0


@dataclass
class SearchStats:
    """Statistics for a single search operation."""
    query: str
    user_id: Optional[int]
    chat_id: Optional[int]
    results_count: int
    search_time_ms: float
    mongo_time_ms: float
    cache_time_ms: float
    rank_time_ms: float
    cache_hit: bool
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ProfileResult:
    """Profiling breakdown for search operations."""
    normalize_ms: float = 0.0
    cache_check_ms: float = 0.0
    mongo_query_ms: float = 0.0
    ranking_ms: float = 0.0
    pagination_ms: float = 0.0
    total_ms: float = 0.0

    def __str__(self) -> str:
        return (
            f"Profile: normalize={self.normalize_ms:.1f}ms, "
            f"cache={self.cache_check_ms:.1f}ms, "
            f"mongo={self.mongo_query_ms:.1f}ms, "
            f"rank={self.ranking_ms:.1f}ms, "
            f"paginate={self.pagination_ms:.1f}ms, "
            f"total={self.total_ms:.1f}ms"
        )


# =============================================================================
# Search Service
# =============================================================================

class SearchService:
    """
    Unified search service for CINE3600 bot.

    Features:
    - Query normalization (removes release tags, punctuation)
    - Result ranking (exact match, starts with, contains, fuzzy)
    - Multi-layer caching (search cache + pagination cache)
    - Search statistics tracking
    - Search suggestions
    - Performance profiling

    Usage:
        service = SearchService()
        response = await service.search("avatar 2009", max_results=10)
        print(f"Found {response.total} results in {response.search_time_ms}ms")
    """

    def __init__(self):
        # Search result cache (query -> results)
        self._search_cache: OrderedDict = OrderedDict()

        # Pagination cache (key -> file_ids list)
        self._pagination_cache: OrderedDict = OrderedDict()

        # Search statistics storage
        self._stats: List[SearchStats] = []
        self._max_stats = 10000  # Keep last 10k searches

        # Popular queries for suggestions
        self._query_counts: Dict[str, int] = {}
        self._max_query_counts = 5000

    # =========================================================================
    # Main Search Method
    # =========================================================================

    async def search(
        self,
        query: str,
        chat_id: Optional[int] = None,
        requester_id: Optional[int] = None,
        file_type: Optional[str] = None,
        max_results: int = 10,
        offset: int = 0,
        filter_mode: bool = False,
        use_cache: bool = True,
        profile: bool = False
    ) -> SearchResponse:
        """
        Execute a search with caching, ranking, and profiling.

        Args:
            query: Search query string
            chat_id: Optional chat/group ID
            requester_id: Optional user ID
            file_type: Filter by file type (video/audio/document)
            max_results: Maximum results per page
            offset: Pagination offset
            filter_mode: Enable filter mode
            use_cache: Use cached results if available
            profile: Enable detailed profiling

        Returns:
            SearchResponse with results and metadata
        """
        start_time = time.perf_counter()
        profile_result = ProfileResult() if profile else None

        # Step 1: Normalize query
        norm_start = time.perf_counter()
        query_normalized = self.normalize(query)
        norm_time = (time.perf_counter() - norm_start) * 1000
        if profile_result:
            profile_result.normalize_ms = norm_time

        # Step 2: Check cache
        cache_start = time.perf_counter()
        cache_key = self._cache_key(chat_id, requester_id, query, file_type, filter_mode)
        cached = self._search_cache.get(cache_key) if use_cache else None
        cache_time = (time.perf_counter() - cache_start) * 1000
        if profile_result:
            profile_result.cache_check_ms = cache_time

        mongo_time = 0.0
        results: List[SearchResult] = []
        total = 0

        if cached and use_cache:
            # Cache hit - use cached results
            all_results = cached["results"]
            total = cached["total"]
            cache_hit = True
        else:
            # Cache miss - query database
            cache_hit = False
            mongo_start = time.perf_counter()

            # Import router here to avoid circular imports
            from database import router
            from database.ia_filterdb import _project_file, FileResult

            # Build filter
            flt = self._build_filter(query_normalized, file_type)
            if flt is None:
                return self._empty_response(query, query_normalized)

            # Query all databases
            files, db_total = await router.find_all(flt)

            mongo_time = (time.perf_counter() - mongo_start) * 1000
            if profile_result:
                profile_result.mongo_query_ms = mongo_time

            # Project fields
            projected = [_project_file(f) for f in files if f]
            total = db_total

            # Convert to SearchResult objects
            all_results = self._to_search_results(projected)

            # Rank results
            rank_start = time.perf_counter()
            all_results = self.rank(all_results, query_normalized)
            rank_time = (time.perf_counter() - rank_start) * 1000
            if profile_result:
                profile_result.ranking_ms = rank_time

            # Cache the results
            self._store_cache(cache_key, all_results, total)

        # Pagination
        page_start = time.perf_counter()
        paginated = self.paginate(all_results if not cache_hit else cached["results"],
                                   max_results, offset)
        pagination_time = (time.perf_counter() - page_start) * 1000
        if profile_result:
            profile_result.pagination_ms = pagination_time

        total_time = (time.perf_counter() - start_time) * 1000
        if profile_result:
            profile_result.total_ms = total_time
            logger.info(profile_result)

        # Determine next offset
        next_offset = str(offset + len(paginated)) if offset + len(paginated) < total else ""

        # Record statistics
        self._record_stats(SearchStats(
            query=query,
            user_id=requester_id,
            chat_id=chat_id,
            results_count=len(paginated),
            search_time_ms=total_time,
            mongo_time_ms=mongo_time,
            cache_time_ms=cache_time,
            rank_time_ms=pagination_time,
            cache_hit=cache_hit
        ))

        # Track query popularity
        self._track_query(query_normalized)

        return SearchResponse(
            results=paginated,
            total=total,
            query=query,
            query_normalized=query_normalized,
            offset=offset,
            next_offset=next_offset,
            cache_hit=cache_hit,
            search_time_ms=total_time,
            mongo_time_ms=mongo_time
        )

    # =========================================================================
    # Query Normalization
    # =========================================================================

    def normalize(self, query: str) -> str:
        """
        Normalize a search query for better matching.

        Removes:
        - Release tags (1080p, BluRay, x265, etc.)
        - Bracketed text [group], (year), {tag}
        - Punctuation and special characters
        - Multiple spaces

        Converts to lowercase.

        Example:
            "Avatar.2009.1080p.BluRay.x265" -> "avatar 2009"
            "The.Matrix.(1999).[AMZN]" -> "the matrix 1999"
        """
        if not query:
            return ""

        text = query.lower()

        # Remove bracketed content
        text = BRACKET_TAG_RE.sub(" ", text)

        # Replace underscores and dots with spaces
        text = text.replace("_", " ").replace(".", " ")

        # Remove release tags
        text = RELEASE_TAG_RE.sub(" ", text)

        # Remove punctuation
        text = NON_WORD_RE.sub(" ", text)

        # Collapse multiple spaces
        text = MULTI_SPACE_RE.sub(" ", text).strip()

        return text

    def extract_year(self, query: str) -> Tuple[str, Optional[int]]:
        """
        Extract year from query if present.

        Returns (query_without_year, year) tuple.
        """
        normalized = self.normalize(query)
        match = YEAR_RE.search(normalized)
        if match:
            year = int(match.group(1))
            query_without_year = YEAR_RE.sub("", normalized).strip()
            return query_without_year, year
        return normalized, None

    # =========================================================================
    # Search Ranking
    # =========================================================================

    def rank(self, results: List[SearchResult], query: str) -> List[SearchResult]:
        """
        Score and rank search results by relevance.

        Scoring:
        - 100: Exact title match
        - 80: Starts with query
        - 60: Contains query as word
        - 40: Same year present
        - 20: Any fuzzy match
        - 10: Caption match

        Results sorted by score (highest first).
        """
        if not results:
            return results

        query_normalized = self.normalize(query)
        query_words = set(query_normalized.split())

        # Extract year from query for bonus scoring
        query_without_year, query_year = self.extract_year(query)

        for result in results:
            result.score = 0
            title = result.file_name_normalized
            title_words = set(title.split())

            # Exact match (100 points)
            if title == query_normalized:
                result.score = 100
                result.match_type = "exact"
                continue

            # Starts with query (80 points)
            if title.startswith(query_normalized):
                result.score = 80
                result.match_type = "starts_with"
                continue

            # Contains query as substring (60 points)
            if query_normalized in title:
                result.score = 60
                result.match_type = "contains"
                continue

            # Query words subset of title words (50 points)
            if query_words and query_words.issubset(title_words):
                result.score = 50
                result.match_type = "word_subset"
                continue

            # Year match bonus (40 points)
            if query_year:
                year_match = YEAR_RE.search(title)
                if year_match and int(year_match.group(1)) == query_year:
                    result.score = max(result.score, 40)
                    result.match_type = "year_match"

            # Caption match (10 points)
            if result.caption and query_normalized in result.caption.lower():
                result.score = max(result.score, 10)
                result.match_type = "caption_match"

            # Fuzzy/partial match (20 points minimum)
            if result.score == 0:
                # Check for partial word matches
                common_words = query_words & title_words
                if common_words:
                    result.score = 20
                    result.match_type = "fuzzy"

        # Sort by score descending
        results.sort(key=lambda r: r.score, reverse=True)
        return results

    # =========================================================================
    # Pagination
    # =========================================================================

    def paginate(
        self,
        results: List[SearchResult],
        max_results: int,
        offset: int = 0
    ) -> List[SearchResult]:
        """
        Slice results for pagination.

        Args:
            results: Full result list
            max_results: Items per page
            offset: Starting index

        Returns:
            Sliced results for current page
        """
        start = max(0, offset)
        end = start + max_results
        return results[start:end]

    def store_pagination(self, key: str, file_ids: List[str]) -> None:
        """Store file IDs for pagination cache."""
        self._pagination_cache[key] = {
            "file_ids": file_ids,
            "created_at": time.monotonic()
        }
        self._pagination_cache.move_to_end(key)
        self._prune_pagination_cache()

    def get_pagination(self, key: str) -> Optional[List[str]]:
        """Get file IDs from pagination cache."""
        cached = self._pagination_cache.get(key)
        if cached:
            age = time.monotonic() - cached["created_at"]
            if age < PAGINATION_CACHE_TTL_SECONDS:
                self._pagination_cache.move_to_end(key)
                return cached["file_ids"]
            else:
                del self._pagination_cache[key]
        return None

    # =========================================================================
    # Caching
    # =========================================================================

    def _cache_key(
        self,
        chat_id: Optional[int],
        requester_id: Optional[int],
        query: str,
        file_type: Optional[str],
        filter_mode: bool
    ) -> str:
        """Generate cache key for search."""
        return "|".join([
            str(chat_id or 0),
            str(requester_id or 0),
            str(int(filter_mode)),
            str(file_type or "*"),
            self.normalize(query)
        ])

    def _store_cache(self, key: str, results: List[SearchResult], total: int) -> None:
        """Store search results in cache."""
        self._search_cache[key] = {
            "results": results,
            "total": total,
            "created_at": time.monotonic()
        }
        self._search_cache.move_to_end(key)
        self._prune_search_cache()

    def get_cached(self, key: str) -> Optional[Dict]:
        """Get cached search results."""
        cached = self._search_cache.get(key)
        if cached:
            age = time.monotonic() - cached["created_at"]
            if age < SEARCH_CACHE_TTL_SECONDS:
                self._search_cache.move_to_end(key)
                return cached
            else:
                del self._search_cache[key]
        return None

    def invalidate_cache(self, query: Optional[str] = None) -> int:
        """
        Invalidate cache entries.

        Args:
            query: Specific query to invalidate, or None for all

        Returns:
            Number of entries removed
        """
        if query:
            query_normalized = self.normalize(query)
            keys_to_remove = [k for k in self._search_cache if query_normalized in k]
            for key in keys_to_remove:
                del self._search_cache[key]
            return len(keys_to_remove)
        else:
            count = len(self._search_cache)
            self._search_cache.clear()
            return count

    def _prune_search_cache(self) -> None:
        """Remove expired and excess cache entries."""
        now = time.monotonic()
        # Remove expired
        expired = [
            k for k, v in self._search_cache.items()
            if now - v["created_at"] > SEARCH_CACHE_TTL_SECONDS
        ]
        for key in expired:
            del self._search_cache[key]

        # Remove excess (LRU)
        while len(self._search_cache) > SEARCH_CACHE_MAX_ENTRIES:
            self._search_cache.popitem(last=False)

    def _prune_pagination_cache(self) -> None:
        """Remove expired pagination cache entries."""
        if len(self._pagination_cache) > SEARCH_CACHE_MAX_ENTRIES:
            # Remove oldest entries
            while len(self._pagination_cache) > SEARCH_CACHE_MAX_ENTRIES:
                self._pagination_cache.popitem(last=False)

    # =========================================================================
    # Search Suggestions
    # =========================================================================

    async def get_suggestions(self, query: str, limit: int = SUGGESTION_LIMIT) -> List[str]:
        """
        Get search suggestions for a query.

        Uses:
        1. Popular queries (prefix match)
        2. Database title prefix search

        Args:
            query: Partial query to suggest for
            limit: Maximum suggestions to return

        Returns:
            List of suggested search queries
        """
        if not query or len(query) < 2:
            return []

        query_normalized = self.normalize(query)
        suggestions = set()

        # 1. Popular queries matching prefix
        for cached_query, count in sorted(
            self._query_counts.items(),
            key=lambda x: x[1],
            reverse=True
        ):
            if cached_query.startswith(query_normalized):
                suggestions.add(cached_query)
                if len(suggestions) >= limit:
                    return list(suggestions)

        # 2. Database prefix search for titles
        try:
            from database import router

            # Build prefix filter
            prefix_pattern = f"^{re.escape(query_normalized)}"
            prefix_regex = re.compile(prefix_pattern, re.IGNORECASE)
            flt = {"file_name_normalized": prefix_regex}

            files, _ = await router.find_all(flt)

            for f in files[:limit]:
                name = f.get("file_name_normalized") or self.normalize(f.get("file_name", ""))
                if name:
                    suggestions.add(name)
                    if len(suggestions) >= limit:
                        break
        except Exception as e:
            logger.debug(f"Suggestion DB query failed: {e}")

        return list(suggestions)[:limit]

    def _track_query(self, query: str) -> None:
        """Track query popularity for suggestions."""
        if not query:
            return
        self._query_counts[query] = self._query_counts.get(query, 0) + 1

        # Prune if too large
        if len(self._query_counts) > self._max_query_counts:
            # Remove least popular
            sorted_queries = sorted(
                self._query_counts.items(),
                key=lambda x: x[1]
            )
            for query, _ in sorted_queries[:len(sorted_queries) // 2]:
                del self._query_counts[query]

    # =========================================================================
    # Statistics
    # =========================================================================

    def _record_stats(self, stats: SearchStats) -> None:
        """Record search statistics."""
        self._stats.append(stats)
        if len(self._stats) > self._max_stats:
            self._stats = self._stats[-self._max_stats:]

    def get_stats(self, limit: int = 100) -> List[SearchStats]:
        """Get recent search statistics."""
        return self._stats[-limit:]

    def get_stats_summary(self) -> Dict[str, Any]:
        """
        Get aggregated statistics summary.

        Returns:
            Summary with avg times, cache hit rate, popular queries
        """
        if not self._stats:
            return {
                "total_searches": 0,
                "avg_search_time_ms": 0,
                "avg_mongo_time_ms": 0,
                "cache_hit_rate": 0,
                "popular_queries": []
            }

        total = len(self._stats)
        cache_hits = sum(1 for s in self._stats if s.cache_hit)

        avg_search = sum(s.search_time_ms for s in self._stats) / total
        avg_mongo = sum(s.mongo_time_ms for s in self._stats) / total

        return {
            "total_searches": total,
            "avg_search_time_ms": round(avg_search, 2),
            "avg_mongo_time_ms": round(avg_mongo, 2),
            "cache_hit_rate": round(cache_hits / total * 100, 2),
            "popular_queries": list(self._query_counts.items())[:10]
        }

    def clear_stats(self) -> None:
        """Clear all statistics."""
        self._stats.clear()

    # =========================================================================
    # Profiling
    # =========================================================================

    async def profile_search(self, query: str) -> Dict[str, float]:
        """
        Profile a search query with detailed timing.

        Returns timing breakdown for:
        - normalize: Query normalization time
        - cache_check: Cache lookup time
        - mongo_query: Database query time
        - ranking: Result ranking time
        - pagination: Result slicing time
        - total: Total search time
        """
        response = await self.search(
            query,
            use_cache=False,
            profile=True
        )

        return {
            "search_time_ms": response.search_time_ms,
            "mongo_time_ms": response.mongo_time_ms,
            "results_count": len(response.results),
            "total_results": response.total,
            "ranking_time_ms": response.rank_time_ms,
            "cache_hit": response.cache_hit
        }

    # =========================================================================
    # Helper Methods
    # =========================================================================

    def _build_filter(self, query: str, file_type: Optional[str] = None) -> Optional[Dict]:
        """Build MongoDB filter for search."""
        if not query:
            return None

        try:
            regex = re.compile(re.escape(query), flags=re.IGNORECASE)
        except Exception as e:
            logger.error(f"Bad search pattern: {e}")
            return None

        flt = {
            "$or": [
                {"file_name_normalized": regex},
                {"file_name": regex}
            ]
        }

        if file_type:
            flt["file_type"] = file_type

        return flt

    def _to_search_results(self, docs: List[Dict]) -> List[SearchResult]:
        """Convert document dicts to SearchResult objects."""
        results = []
        for doc in docs:
            if not doc:
                continue
            try:
                results.append(SearchResult(
                    file_id=doc.get("_id", ""),
                    file_name=doc.get("file_name", ""),
                    file_name_normalized=doc.get("file_name_normalized", ""),
                    file_size=doc.get("file_size", 0),
                    file_type=doc.get("file_type", ""),
                    caption=doc.get("caption"),
                    file_ref=doc.get("file_ref")
                ))
            except Exception as e:
                logger.debug(f"Failed to convert doc: {e}")
        return results

    def _empty_response(self, query: str, query_normalized: str) -> SearchResponse:
        """Return empty search response."""
        return SearchResponse(
            results=[],
            total=0,
            query=query,
            query_normalized=query_normalized,
            offset=0,
            next_offset="",
            cache_hit=False,
            search_time_ms=0.0
        )


# =============================================================================
# Global Instance
# =============================================================================

# Singleton instance for global use
_search_service: Optional[SearchService] = None


def get_search_service() -> SearchService:
    """Get or create the global SearchService instance."""
    global _search_service
    if _search_service is None:
        _search_service = SearchService()
    return _search_service


def reset_search_service() -> None:
    """Reset the global SearchService instance (for testing)."""
    global _search_service
    _search_service = None
