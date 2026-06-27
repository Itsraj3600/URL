"""
Pagination Service

Handles pagination of search results with intelligent caching.
Eliminates redundant database queries for paginated results.

Features:
- Store full result sets in cache
- Slice results for pagination
- Handle large result sets efficiently
- Track pagination state
"""

import logging
import time
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from collections import OrderedDict

logger = logging.getLogger(__name__)

DEFAULT_PAGE_SIZE = 10
MAX_PAGE_SIZE = 50
PAGINATION_TTL_SECONDS = 900  # 15 minutes


@dataclass
class PageResult:
    """A single page of results."""
    items: List[Any]
    page_number: int
    total_pages: int
    total_items: int
    has_next: bool
    has_prev: bool
    start_index: int
    end_index: int


@dataclass
class PaginationState:
    """State for a paginated result set."""
    key: str
    total_items: int
    page_size: int
    created_at: float
    last_accessed: float
    hits: int = 0


class PaginationService:
    """
    Service for efficient result pagination.

    Instead of querying the database for each page,
    stores the result IDs and slices them for pagination.

    Usage:
        # First search - stores IDs
        state = await pagination_service.store_results(
            key="user123:avatar",
            results=[file1, file2, file3, ...],
            page_size=10
        )

        # Subsequent pages - no DB query needed
        page = await pagination_service.get_page(
            key="user123:avatar",
            page=2
        )
    """

    def __init__(
        self,
        default_page_size: int = DEFAULT_PAGE_SIZE,
        max_page_size: int = MAX_PAGE_SIZE,
        ttl_seconds: int = PAGINATION_TTL_SECONDS,
        max_entries: int = 1000
    ):
        self.default_page_size = default_page_size
        self.max_page_size = max_page_size
        self.ttl_seconds = ttl_seconds
        self.max_entries = max_entries

        # Store pagination metadata
        self._states: Dict[str, PaginationState] = {}

        # Store result IDs (key -> list of IDs)
        self._results_cache: OrderedDict = OrderedDict()

        # Store actual result objects (key -> list of objects)
        self._objects_cache: OrderedDict = OrderedDict()

    def store_results(
        self,
        key: str,
        results: List[Any],
        page_size: Optional[int] = None,
        id_field: str = "file_id"
    ) -> PaginationState:
        """
        Store search results for pagination.

        Args:
            key: Unique key for this result set
            results: List of result objects (SearchResult or dict)
            page_size: Items per page (uses default if None)
            id_field: Field to use as ID for objects

        Returns:
            PaginationState with metadata
        """
        page_size = min(page_size or self.default_page_size, self.max_page_size)
        now = time.monotonic()

        # Extract IDs
        ids = []
        for r in results:
            if isinstance(r, dict):
                ids.append(r.get(id_field, r.get("_id", str(r))))
            elif hasattr(r, id_field):
                ids.append(getattr(r, id_field))
            elif hasattr(r, "file_id"):
                ids.append(r.file_id)
            else:
                ids.append(str(r))

        # Store IDs and objects
        self._results_cache[key] = {
            "ids": ids,
            "created_at": now
        }
        self._results_cache.move_to_end(key)

        self._objects_cache[key] = {
            "results": results,
            "created_at": now
        }
        self._objects_cache.move_to_end(key)

        # Create state
        state = PaginationState(
            key=key,
            total_items=len(results),
            page_size=page_size,
            created_at=now,
            last_accessed=now
        )
        self._states[key] = state

        # Prune if needed
        self._prune_if_needed()

        return state

    def get_page(
        self,
        key: str,
        page: int = 1,
        page_size: Optional[int] = None
    ) -> Optional[PageResult]:
        """
        Get a specific page of results.

        Args:
            key: Key from store_results
            page: Page number (1-indexed)
            page_size: Override page size

        Returns:
            PageResult with items and metadata, or None if key expired
        """
        # Check if we have this key
        cached = self._objects_cache.get(key)
        if not cached:
            return None

        # Check expiration
        now = time.monotonic()
        if now - cached["created_at"] > self.ttl_seconds:
            self._cleanup_key(key)
            return None

        # Get state
        state = self._states.get(key)
        if not state:
            return None

        # Update access time
        state.last_accessed = now
        state.hits += 1

        # Get results
        results = cached["results"]
        page_size = page_size or state.page_size
        total_items = len(results)
        total_pages = (total_items + page_size - 1) // page_size

        # Validate page
        if page < 1:
            page = 1
        elif page > total_pages:
            page = total_pages

        # Calculate slice
        start_index = (page - 1) * page_size
        end_index = min(start_index + page_size, total_items)

        # Slice results
        items = results[start_index:end_index]

        return PageResult(
            items=items,
            page_number=page,
            total_pages=total_pages,
            total_items=total_items,
            has_next=page < total_pages,
            has_prev=page > 1,
            start_index=start_index,
            end_index=end_index
        )

    def get_page_by_offset(
        self,
        key: str,
        offset: int = 0,
        limit: Optional[int] = None
    ) -> Optional[PageResult]:
        """
        Get results by offset instead of page number.

        Args:
            key: Key from store_results
            offset: Starting index (0-indexed)
            limit: Max items to return

        Returns:
            PageResult with items and metadata
        """
        cached = self._objects_cache.get(key)
        if not cached:
            return None

        now = time.monotonic()
        if now - cached["created_at"] > self.ttl_seconds:
            self._cleanup_key(key)
            return None

        state = self._states.get(key)
        if not state:
            return None

        state.last_accessed = now
        state.hits += 1

        results = cached["results"]
        limit = limit or state.page_size
        total_items = len(results)
        page_size = limit

        # Validate offset
        if offset < 0:
            offset = 0
        elif offset >= total_items:
            return PageResult(
                items=[],
                page_number=(offset // page_size) + 1 if total_items > 0 else 1,
                total_pages=(total_items + page_size - 1) // page_size if total_items > 0 else 1,
                total_items=total_items,
                has_next=False,
                has_prev=offset > 0,
                start_index=offset,
                end_index=offset
            )

        # Calculate page
        page = (offset // page_size) + 1
        end_index = min(offset + limit, total_items)

        items = results[offset:end_index]
        total_pages = (total_items + page_size - 1) // page_size

        return PageResult(
            items=items,
            page_number=page,
            total_pages=total_pages,
            total_items=total_items,
            has_next=end_index < total_items,
            has_prev=offset > 0,
            start_index=offset,
            end_index=end_index
        )

    def get_result_ids(self, key: str) -> Optional[List[str]]:
        """Get just the IDs from stored results."""
        cached = self._results_cache.get(key)
        if not cached:
            return None

        now = time.monotonic()
        if now - cached["created_at"] > self.ttl_seconds:
            self._cleanup_key(key)
            return None

        return cached["ids"]

    def get_total_items(self, key: str) -> int:
        """Get total items without loading results."""
        state = self._states.get(key)
        if state:
            return state.total_items
        return 0

    def has_results(self, key: str) -> bool:
        """Check if results exist for key."""
        if key not in self._objects_cache:
            return False

        cached = self._objects_cache.get(key)
        if not cached:
            return False

        now = time.monotonic()
        if now - cached["created_at"] > self.ttl_seconds:
            self._cleanup_key(key)
            return False

        return True

    def invalidate(self, key: str) -> bool:
        """Remove stored results for key."""
        return self._cleanup_key(key)

    def invalidate_pattern(self, pattern: str) -> int:
        """Remove all keys matching pattern."""
        import fnmatch
        count = 0
        for key in list(self._states.keys()):
            if fnmatch.fnmatch(key, pattern):
                self._cleanup_key(key)
                count += 1
        return count

    def clear(self) -> int:
        """Clear all pagination data."""
        count = len(self._states)
        self._states.clear()
        self._results_cache.clear()
        self._objects_cache.clear()
        return count

    def _cleanup_key(self, key: str) -> bool:
        """Remove all data for a key."""
        if key in self._states:
            del self._states[key]
        if key in self._results_cache:
            del self._results_cache[key]
        if key in self._objects_cache:
            del self._objects_cache[key]
        return True

    def _prune_if_needed(self) -> None:
        """Remove oldest entries if over limit."""
        # Remove expired entries first
        now = time.monotonic()
        expired = [
            k for k, v in self._objects_cache.items()
            if now - v["created_at"] > self.ttl_seconds
        ]
        for key in expired:
            self._cleanup_key(key)

        # Remove oldest if still over limit
        while len(self._states) > self.max_entries:
            if self._objects_cache:
                oldest_key = next(iter(self._objects_cache))
                self._cleanup_key(oldest_key)
            else:
                break

    def get_stats(self) -> Dict[str, Any]:
        """Get pagination service statistics."""
        return {
            "total_stored": len(self._states),
            "max_entries": self.max_entries,
            "ttl_seconds": self.ttl_seconds,
            "total_hits": sum(s.hits for s in self._states.values()),
            "keys": list(self._states.keys())[:10]
        }


# =============================================================================
# Global Instance
# =============================================================================

_pagination_service: Optional[PaginationService] = None


def get_pagination_service() -> PaginationService:
    """Get or create the global PaginationService instance."""
    global _pagination_service
    if _pagination_service is None:
        _pagination_service = PaginationService()
    return _pagination_service


def reset_pagination_service() -> None:
    """Reset the global PaginationService instance."""
    global _pagination_service
    _pagination_service = None
