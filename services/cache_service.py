"""
Cache Service

A unified caching layer that supports:
- In-memory caching (fastest)
- Redis caching (optional, distributed)
- TTL-based expiration
- LRU eviction
- Cache statistics

This service can be used by SearchService, PaginationService, etc.
"""

import logging
import time
import json
from collections import OrderedDict
from typing import Any, Dict, Optional, Generic, TypeVar, Callable
from dataclasses import dataclass, field
from datetime import datetime
from functools import wraps

logger = logging.getLogger(__name__)

T = TypeVar('T')


@dataclass
class CacheEntry:
    """A single cache entry with metadata."""
    value: Any
    created_at: float
    expires_at: float
    hits: int = 0
    size_bytes: int = 0


@dataclass
class CacheStats:
    """Cache statistics."""
    total_entries: int = 0
    total_hits: int = 0
    total_misses: int = 0
    total_evictions: int = 0
    total_size_bytes: int = 0
    avg_hit_time_ms: float = 0.0
    avg_miss_time_ms: float = 0.0


class MemoryCache:
    """
    In-memory LRU cache with TTL support.

    Features:
    - O(1) get/set operations
    - TTL-based expiration
    - LRU eviction when full
    - Size tracking
    - Statistics
    """

    def __init__(
        self,
        max_entries: int = 1000,
        default_ttl_seconds: int = 600,
        max_size_mb: float = 100.0
    ):
        self.max_entries = max_entries
        self.default_ttl = default_ttl_seconds
        self.max_size_bytes = int(max_size_mb * 1024 * 1024)

        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._stats = CacheStats()
        self._hit_times: list = []
        self._miss_times: list = []

    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.

        Returns None if key doesn't exist or expired.
        """
        start = time.perf_counter()
        entry = self._cache.get(key)

        if entry is None:
            self._stats.total_misses += 1
            self._miss_times.append((time.perf_counter() - start) * 1000)
            return None

        # Check expiration
        if time.monotonic() > entry.expires_at:
            del self._cache[key]
            self._stats.total_misses += 1
            self._stats.total_evictions += 1
            self._miss_times.append((time.perf_counter() - start) * 1000)
            return None

        # Cache hit - move to end (most recently used)
        entry.hits += 1
        self._stats.total_hits += 1
        self._cache.move_to_end(key)
        self._hit_times.append((time.perf_counter() - start) * 1000)

        return entry.value

    def set(
        self,
        key: str,
        value: Any,
        ttl_seconds: Optional[int] = None,
        size_bytes: int = 0
    ) -> None:
        """Set value in cache with optional TTL."""
        ttl = ttl_seconds or self.default_ttl
        now = time.monotonic()

        # Estimate size if not provided
        if size_bytes == 0:
            try:
                size_bytes = len(json.dumps(value))
            except Exception:
                size_bytes = 1024  # Default estimate

        # Remove existing entry if present
        if key in self._cache:
            old_entry = self._cache[key]
            self._stats.total_size_bytes -= old_entry.size_bytes

        # Create new entry
        entry = CacheEntry(
            value=value,
            created_at=now,
            expires_at=now + ttl,
            size_bytes=size_bytes
        )

        # Check size limits
        self._prune_if_needed(entry.size_bytes)

        # Add to cache
        self._cache[key] = entry
        self._cache.move_to_end(key)
        self._stats.total_size_bytes += size_bytes
        self._stats.total_entries = len(self._cache)

    def delete(self, key: str) -> bool:
        """Delete entry from cache. Returns True if existed."""
        if key in self._cache:
            entry = self._cache[key]
            self._stats.total_size_bytes -= entry.size_bytes
            del self._cache[key]
            self._stats.total_entries = len(self._cache)
            return True
        return False

    def clear(self) -> int:
        """Clear all entries. Returns count cleared."""
        count = len(self._cache)
        self._cache.clear()
        self._stats.total_size_bytes = 0
        self._stats.total_entries = 0
        return count

    def exists(self, key: str) -> bool:
        """Check if key exists and is not expired."""
        entry = self._cache.get(key)
        if entry is None:
            return False
        if time.monotonic() > entry.expires_at:
            del self._cache[key]
            return False
        return True

    def get_or_set(
        self,
        key: str,
        factory: Callable[[], T],
        ttl_seconds: Optional[int] = None
    ) -> T:
        """
        Get value from cache, or compute and store if missing.

        Args:
            key: Cache key
            factory: Function to compute value if missing
            ttl_seconds: TTL for new entry

        Returns:
            Cached or computed value
        """
        value = self.get(key)
        if value is not None:
            return value

        value = factory()
        self.set(key, value, ttl_seconds)
        return value

    def invalidate_pattern(self, pattern: str) -> int:
        """
        Invalidate all keys matching pattern.

        Args:
            pattern: Glob-style pattern (e.g., "search:*")

        Returns:
            Count of keys removed
        """
        import fnmatch
        keys_to_remove = [
            k for k in self._cache.keys()
            if fnmatch.fnmatch(k, pattern)
        ]
        for key in keys_to_remove:
            self.delete(key)
        return len(keys_to_remove)

    def _prune_if_needed(self, incoming_size: int) -> None:
        """Prune cache if adding new entry would exceed limits."""
        # Prune by count
        while len(self._cache) >= self.max_entries:
            self._evict_oldest()

        # Prune by size
        while (
            self._stats.total_size_bytes + incoming_size > self.max_size_bytes
            and len(self._cache) > 0
        ):
            self._evict_oldest()

        # Prune expired entries
        now = time.monotonic()
        expired = [
            k for k, v in self._cache.items()
            if now > v.expires_at
        ]
        for key in expired:
            self.delete(key)
            self._stats.total_evictions += 1

    def _evict_oldest(self) -> None:
        """Evict the oldest (least recently used) entry."""
        if self._cache:
            key, entry = self._cache.popitem(last=False)
            self._stats.total_size_bytes -= entry.size_bytes
            self._stats.total_evictions += 1

    def get_stats(self) -> CacheStats:
        """Get cache statistics."""
        stats = CacheStats(
            total_entries=len(self._cache),
            total_hits=self._stats.total_hits,
            total_misses=self._stats.total_misses,
            total_evictions=self._stats.total_evictions,
            total_size_bytes=self._stats.total_size_bytes
        )

        if self._hit_times:
            stats.avg_hit_time_ms = sum(self._hit_times[-100:]) / len(self._hit_times[-100:])
        if self._miss_times:
            stats.avg_miss_time_ms = sum(self._miss_times[-100:]) / len(self._miss_times[-100:])

        return stats

    def get_hit_rate(self) -> float:
        """Get cache hit rate (0.0 to 1.0)."""
        total = self._stats.total_hits + self._stats.total_misses
        if total == 0:
            return 0.0
        return self._stats.total_hits / total


class CacheService:
    """
    Unified cache service with multiple cache namespaces.

    Provides separate caches for:
    - search: Search results
    - pagination: File ID lists for pagination
    - metadata: File metadata
    - session: User session data
    """

    def __init__(
        self,
        search_ttl: int = 600,
        pagination_ttl: int = 900,
        metadata_ttl: int = 3600,
        session_ttl: int = 1800,
        max_entries_per_cache: int = 500
    ):
        self.caches = {
            "search": MemoryCache(max_entries=max_entries_per_cache, default_ttl_seconds=search_ttl),
            "pagination": MemoryCache(max_entries=max_entries_per_cache, default_ttl_seconds=pagination_ttl),
            "metadata": MemoryCache(max_entries=max_entries_per_cache, default_ttl_seconds=metadata_ttl),
            "session": MemoryCache(max_entries=max_entries_per_cache, default_ttl_seconds=session_ttl),
        }

    def get_search(self, key: str) -> Optional[Any]:
        """Get from search cache."""
        return self.caches["search"].get(key)

    def set_search(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set in search cache."""
        self.caches["search"].set(key, value, ttl)

    def get_pagination(self, key: str) -> Optional[Any]:
        """Get from pagination cache."""
        return self.caches["pagination"].get(key)

    def set_pagination(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set in pagination cache."""
        self.caches["pagination"].set(key, value, ttl)

    def get_metadata(self, key: str) -> Optional[Any]:
        """Get from metadata cache."""
        return self.caches["metadata"].get(key)

    def set_metadata(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set in metadata cache."""
        self.caches["metadata"].set(key, value, ttl)

    def get_session(self, key: str) -> Optional[Any]:
        """Get from session cache."""
        return self.caches["session"].get(key)

    def set_session(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set in session cache."""
        self.caches["session"].set(key, value, ttl)

    def invalidate_search(self, pattern: str = "*") -> int:
        """Invalidate search cache entries."""
        if pattern == "*":
            return self.caches["search"].clear()
        return self.caches["search"].invalidate_pattern(pattern)

    def invalidate_all(self) -> Dict[str, int]:
        """Clear all caches."""
        return {
            name: cache.clear()
            for name, cache in self.caches.items()
        }

    def get_all_stats(self) -> Dict[str, CacheStats]:
        """Get statistics for all caches."""
        return {
            name: cache.get_stats()
            for name, cache in self.caches.items()
        }

    def get_total_hit_rate(self) -> float:
        """Get combined hit rate across all caches."""
        total_hits = sum(s.total_hits for s in self.get_all_stats().values())
        total_misses = sum(s.total_misses for s in self.get_all_stats().values())
        total = total_hits + total_misses
        if total == 0:
            return 0.0
        return total_hits / total


# =============================================================================
# Global Instance
# =============================================================================

_cache_service: Optional[CacheService] = None


def get_cache_service() -> CacheService:
    """Get or create the global CacheService instance."""
    global _cache_service
    if _cache_service is None:
        _cache_service = CacheService()
    return _cache_service


def reset_cache_service() -> None:
    """Reset the global CacheService instance."""
    global _cache_service
    _cache_service = None
