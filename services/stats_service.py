"""
Statistics Service

Tracks search analytics and bot performance metrics.

Features:
- Search statistics (queries, times, results)
- User activity tracking
- Popular queries
- Performance metrics
- Export for dashboard
"""

import logging
import time
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional
from collections import defaultdict, Counter
import json

logger = logging.getLogger(__name__)

MAX_STATS_ENTRIES = 10000
MAX_QUERY_HISTORY = 5000


@dataclass
class SearchMetric:
    """Single search operation metric."""
    query: str
    query_normalized: str
    user_id: Optional[int]
    chat_id: Optional[int]
    results_count: int
    search_time_ms: float
    mongo_time_ms: float
    cache_hit: bool
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class QueryStat:
    """Statistics for a specific query."""
    query: str
    count: int = 0
    avg_time_ms: float = 0.0
    total_time_ms: float = 0.0
    cache_hits: int = 0
    last_searched: datetime = field(default_factory=datetime.utcnow)


@dataclass
class UserStat:
    """Statistics for a specific user."""
    user_id: int
    search_count: int = 0
    last_active: datetime = field(default_factory=datetime.utcnow)


@dataclass
class HourlyStats:
    """Aggregated hourly statistics."""
    hour: datetime
    total_searches: int = 0
    avg_search_time_ms: float = 0.0
    cache_hit_rate: float = 0.0
    unique_users: int = 0
    popular_queries: List[str] = field(default_factory=list)


class StatsService:
    """
    Service for tracking search and bot statistics.

    Usage:
        stats = get_stats_service()

        # Record a search
        stats.record_search(
            query="avatar",
            user_id=12345,
            results_count=10,
            search_time_ms=150,
            cache_hit=True
        )

        # Get reports
        stats.get_popular_queries(limit=10)
        stats.get_performance_summary()
    """

    def __init__(
        self,
        max_entries: int = MAX_STATS_ENTRIES,
        max_query_history: int = MAX_QUERY_HISTORY
    ):
        self.max_entries = max_entries
        self.max_query_history = max_query_history

        # Raw metrics storage
        self._metrics: List[SearchMetric] = []

        # Aggregated query stats
        self._query_stats: Dict[str, QueryStat] = {}

        # User stats
        self._user_stats: Dict[int, UserStat] = {}

        # Hourly aggregations
        self._hourly_stats: Dict[str, HourlyStats] = {}

        # Popular queries cache
        self._popular_queries_cache: List[str] = []
        self._cache_valid = False

    # =========================================================================
    # Recording
    # =========================================================================

    def record_search(
        self,
        query: str,
        query_normalized: Optional[str] = None,
        user_id: Optional[int] = None,
        chat_id: Optional[int] = None,
        results_count: int = 0,
        search_time_ms: float = 0.0,
        mongo_time_ms: float = 0.0,
        cache_hit: bool = False
    ) -> None:
        """Record a search operation metric."""
        now = datetime.utcnow()

        # Normalize if not provided
        if query_normalized is None:
            from services.search_service import get_search_service
            ss = get_search_service()
            query_normalized = ss.normalize(query)

        # Create metric
        metric = SearchMetric(
            query=query,
            query_normalized=query_normalized,
            user_id=user_id,
            chat_id=chat_id,
            results_count=results_count,
            search_time_ms=search_time_ms,
            mongo_time_ms=mongo_time_ms,
            cache_hit=cache_hit,
            timestamp=now
        )

        # Store metric
        self._metrics.append(metric)
        if len(self._metrics) > self.max_entries:
            # Remove oldest 10%
            self._metrics = self._metrics[int(self.max_entries * 0.1):]

        # Update query stats
        self._update_query_stats(metric)

        # Update user stats
        if user_id:
            self._update_user_stats(user_id, now)

        # Update hourly stats
        self._update_hourly_stats(metric, now)

        # Invalidate cache
        self._cache_valid = False

    def _update_query_stats(self, metric: SearchMetric) -> None:
        """Update aggregated query statistics."""
        query = metric.query_normalized
        if not query:
            return

        if query not in self._query_stats:
            self._query_stats[query] = QueryStat(query=query)

        stat = self._query_stats[query]
        stat.count += 1
        stat.total_time_ms += metric.search_time_ms
        stat.avg_time_ms = stat.total_time_ms / stat.count
        stat.last_searched = metric.timestamp

        if metric.cache_hit:
            stat.cache_hits += 1

        # Prune if too many queries
        if len(self._query_stats) > self.max_query_history:
            # Remove least searched
            sorted_queries = sorted(
                self._query_stats.items(),
                key=lambda x: x[1].count
            )
            for q, _ in sorted_queries[:len(sorted_queries) // 2]:
                del self._query_stats[q]

    def _update_user_stats(self, user_id: int, timestamp: datetime) -> None:
        """Update user activity statistics."""
        if user_id not in self._user_stats:
            self._user_stats[user_id] = UserStat(user_id=user_id)

        stat = self._user_stats[user_id]
        stat.search_count += 1
        stat.last_active = timestamp

    def _update_hourly_stats(self, metric: SearchMetric, timestamp: datetime) -> None:
        """Update hourly aggregations."""
        hour_key = timestamp.strftime("%Y-%m-%d-%H")

        if hour_key not in self._hourly_stats:
            self._hourly_stats[hour_key] = HourlyStats(
                hour=timestamp.replace(minute=0, second=0, microsecond=0)
            )

        hourly = self._hourly_stats[hour_key]
        hourly.total_searches += 1

        # Running average for search time
        hourly.avg_search_time_ms = (
            (hourly.avg_search_time_ms * (hourly.total_searches - 1) + metric.search_time_ms)
            / hourly.total_searches
        )

        if metric.cache_hit:
            hourly.cache_hit_rate = (
                (hourly.cache_hit_rate * (hourly.total_searches - 1) + 1)
                / hourly.total_searches
            )
        else:
            hourly.cache_hit_rate = (
                hourly.cache_hit_rate * (hourly.total_searches - 1)
                / hourly.total_searches
            )

        # Track unique users per hour
        # (simplified - just counting user searches)
        hourly.unique_users = len(self._user_stats)

    # =========================================================================
    # Reports
    # =========================================================================

    def get_popular_queries(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most searched queries."""
        if not self._cache_valid or len(self._popular_queries_cache) < limit:
            sorted_queries = sorted(
                self._query_stats.items(),
                key=lambda x: x[1].count,
                reverse=True
            )[:limit]

            self._popular_queries_cache = [
                {
                    "query": query,
                    "count": stat.count,
                    "avg_time_ms": round(stat.avg_time_ms, 2),
                    "cache_hit_rate": round(stat.cache_hits / stat.count * 100, 1) if stat.count > 0 else 0
                }
                for query, stat in sorted_queries
            ]
            self._cache_valid = True

        return self._popular_queries_cache[:limit]

    def get_performance_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get performance summary for the last N hours."""
        now = datetime.utcnow()
        cutoff = now - timedelta(hours=hours)

        # Filter recent metrics
        recent_metrics = [
            m for m in self._metrics
            if m.timestamp >= cutoff
        ]

        if not recent_metrics:
            return {
                "period_hours": hours,
                "total_searches": 0,
                "avg_search_time_ms": 0,
                "avg_mongo_time_ms": 0,
                "cache_hit_rate": 0,
                "avg_results_count": 0,
                "unique_users": 0
            }

        total = len(recent_metrics)
        avg_search = sum(m.search_time_ms for m in recent_metrics) / total
        avg_mongo = sum(m.mongo_time_ms for m in recent_metrics) / total
        cache_hits = sum(1 for m in recent_metrics if m.cache_hit)
        avg_results = sum(m.results_count for m in recent_metrics) / total
        unique_users = len(set(m.user_id for m in recent_metrics if m.user_id))

        return {
            "period_hours": hours,
            "total_searches": total,
            "avg_search_time_ms": round(avg_search, 2),
            "avg_mongo_time_ms": round(avg_mongo, 2),
            "cache_hit_rate": round(cache_hits / total * 100, 2),
            "avg_results_count": round(avg_results, 2),
            "unique_users": unique_users
        }

    def get_hourly_breakdown(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get hourly breakdown of searches."""
        now = datetime.utcnow()
        cutoff = now - timedelta(hours=hours)

        relevant_hours = {
            k: v for k, v in self._hourly_stats.items()
            if v.hour >= cutoff
        }

        return [
            {
                "hour": stat.hour.isoformat(),
                "total_searches": stat.total_searches,
                "avg_search_time_ms": round(stat.avg_search_time_ms, 2),
                "cache_hit_rate": round(stat.cache_hit_rate * 100, 2)
            }
            for stat in sorted(
                relevant_hours.values(),
                key=lambda x: x.hour
            )
        ]

    def get_user_stats(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get statistics for a specific user."""
        stat = self._user_stats.get(user_id)
        if not stat:
            return None

        return {
            "user_id": user_id,
            "search_count": stat.search_count,
            "last_active": stat.last_active.isoformat()
        }

    def get_top_users(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most active users."""
        sorted_users = sorted(
            self._user_stats.items(),
            key=lambda x: x[1].search_count,
            reverse=True
        )[:limit]

        return [
            {
                "user_id": user_id,
                "search_count": stat.search_count,
                "last_active": stat.last_active.isoformat()
            }
            for user_id, stat in sorted_users
        ]

    def get_cache_efficiency(self) -> Dict[str, Any]:
        """Get cache efficiency metrics."""
        if not self._metrics:
            return {
                "total_searches": 0,
                "cache_hits": 0,
                "cache_misses": 0,
                "hit_rate": 0,
                "estimated_time_saved_ms": 0
            }

        total = len(self._metrics)
        hits = sum(1 for m in self._metrics if m.cache_hit)
        misses = total - hits
        hit_rate = hits / total if total > 0 else 0

        # Estimate time saved (mongo time for cache hits)
        avg_mongo_time = sum(m.mongo_time_ms for m in self._metrics) / total
        estimated_saved = hits * avg_mongo_time

        return {
            "total_searches": total,
            "cache_hits": hits,
            "cache_misses": misses,
            "hit_rate": round(hit_rate * 100, 2),
            "estimated_time_saved_ms": round(estimated_saved, 2)
        }

    # =========================================================================
    # Export
    # =========================================================================

    def export_stats(self, format: str = "dict") -> Any:
        """
        Export all statistics for dashboard.

        Args:
            format: "dict", "json"

        Returns:
            Complete stats dictionary or JSON string
        """
        data = {
            "timestamp": datetime.utcnow().isoformat(),
            "performance": self.get_performance_summary(),
            "popular_queries": self.get_popular_queries(),
            "hourly_breakdown": self.get_hourly_breakdown(),
            "cache_efficiency": self.get_cache_efficiency(),
            "top_users": self.get_top_users(),
            "totals": {
                "total_searches": len(self._metrics),
                "unique_queries": len(self._query_stats),
                "unique_users": len(self._user_stats)
            }
        }

        if format == "json":
            return json.dumps(data, default=str, indent=2)
        return data

    # =========================================================================
    # Cleanup
    # =========================================================================

    def clear_stats(self) -> None:
        """Clear all statistics."""
        self._metrics.clear()
        self._query_stats.clear()
        self._user_stats.clear()
        self._hourly_stats.clear()
        self._popular_queries_cache = []
        self._cache_valid = False

    def prune_old_stats(self, days: int = 7) -> int:
        """Remove stats older than N days."""
        cutoff = datetime.utcnow() - timedelta(days=days)

        original_len = len(self._metrics)
        self._metrics = [m for m in self._metrics if m.timestamp >= cutoff]

        return original_len - len(self._metrics)


# =============================================================================
# Global Instance
# =============================================================================

_stats_service: Optional[StatsService] = None


def get_stats_service() -> StatsService:
    """Get or create the global StatsService instance."""
    global _stats_service
    if _stats_service is None:
        _stats_service = StatsService()
    return _stats_service


def reset_stats_service() -> None:
    """Reset the global StatsService instance."""
    global _stats_service
    _stats_service = None
