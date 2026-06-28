"""
Index Statistics Service

Tracks comprehensive statistics for indexing operations.

Features:
- Per-job statistics
- Aggregate statistics
- Speed analysis
- Error tracking
- Historical data
- Export for dashboard
"""

import logging
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional
from collections import defaultdict
import json

logger = logging.getLogger(__name__)


@dataclass
class JobStatistics:
    """Statistics for a single job."""
    job_id: str
    channel_id: int
    channel_name: str = ""

    # Timing
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: float = 0.0

    # Counts
    processed: int = 0
    inserted: int = 0
    duplicates: int = 0
    errors: int = 0
    skipped_no_media: int = 0
    skipped_unsupported: int = 0
    skipped_deleted: int = 0

    # Speed
    avg_speed: float = 0.0  # files/sec
    peak_speed: float = 0.0
    slowest_speed: float = 0.0

    # Batch info
    total_batches: int = 0
    avg_batch_size: float = 0.0

    # Status
    status: str = "completed"
    error_message: Optional[str] = None


@dataclass
class AggregateStats:
    """Aggregate statistics across all jobs."""
    # Totals
    total_jobs: int = 0
    completed_jobs: int = 0
    failed_jobs: int = 0
    cancelled_jobs: int = 0

    # Files
    total_files_indexed: int = 0
    total_duplicates: int = 0
    total_errors: int = 0
    total_skipped: int = 0

    # Speed
    avg_speed: float = 0.0
    peak_speed: float = 0.0
    fastest_job_speed: float = 0.0

    # Time
    total_indexing_time_seconds: float = 0.0
    avg_job_duration_seconds: float = 0.0
    fastest_job_seconds: float = 0.0
    slowest_job_seconds: float = 0.0

    # Channels
    unique_channels_indexed: int = 0
    largest_channel_files: int = 0
    largest_channel_name: str = ""

    # Period stats
    files_today: int = 0
    files_this_week: int = 0
    files_this_month: int = 0

    # Errors
    most_common_error: str = ""
    error_rate: float = 0.0


@dataclass
class DailyStats:
    """Statistics for a single day."""
    date: str  # YYYY-MM-DD
    jobs: int = 0
    files_indexed: int = 0
    total_time_seconds: float = 0.0
    avg_speed: float = 0.0
    errors: int = 0


class IndexStatsService:
    """
    Service for tracking indexing statistics.

    Usage:
        stats = get_index_stats_service()

        # Record completed job
        stats.record_job(job_stats)

        # Get reports
        stats.get_aggregate_stats()
        stats.get_recent_jobs(limit=10)
        stats.get_daily_stats(days=7)
    """

    def __init__(self, max_history: int = 1000):
        self.max_history = max_history

        # Job statistics storage
        self._job_stats: Dict[str, JobStatistics] = {}

        # Daily aggregates
        self._daily_stats: Dict[str, DailyStats] = {}

        # Channel statistics
        self._channel_stats: Dict[int, Dict] = defaultdict(lambda: {
            "jobs": 0,
            "files": 0,
            "errors": 0,
            "total_time": 0.0
        })

        # Speed history for averaging
        self._speed_samples: List[float] = []

        # Error tracking
        self._errors: Dict[str, int] = defaultdict(int)

    # =========================================================================
    # Recording
    # =========================================================================

    def record_job(self, stats: JobStatistics) -> None:
        """Record statistics from a completed job."""
        self._job_stats[stats.job_id] = stats

        # Prune old records
        if len(self._job_stats) > self.max_history:
            oldest = list(self._job_stats.keys())[:self.max_history // 2]
            for key in oldest:
                del self._job_stats[key]

        # Update channel stats
        self._channel_stats[stats.channel_id]["jobs"] += 1
        self._channel_stats[stats.channel_id]["files"] += stats.inserted
        self._channel_stats[stats.channel_id]["errors"] += stats.errors
        self._channel_stats[stats.channel_id]["total_time"] += stats.duration_seconds

        # Update daily stats
        if stats.completed_at:
            date_key = stats.completed_at.strftime("%Y-%m-%d")
            daily = self._daily_stats.get(date_key, DailyStats(date=date_key))
            daily.jobs += 1
            daily.files_indexed += stats.inserted
            daily.total_time_seconds += stats.duration_seconds
            daily.errors += stats.errors
            self._daily_stats[date_key] = daily

        # Track speed
        if stats.avg_speed > 0:
            self._speed_samples.append(stats.avg_speed)
            if len(self._speed_samples) > 500:
                self._speed_samples = self._speed_samples[-500:]

    def record_error(self, error_type: str) -> None:
        """Record an error occurrence."""
        self._errors[error_type] += 1

    # =========================================================================
    # Reports
    # =========================================================================

    def get_aggregate_stats(self) -> AggregateStats:
        """Get aggregated statistics."""
        now = datetime.utcnow()
        today = now.date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)

        stats = AggregateStats()

        # Count jobs and calculate totals
        durations = []
        speeds = []
        completed_files = 0

        for job in self._job_stats.values():
            stats.total_jobs += 1

            if job.status == "completed":
                stats.completed_jobs += 1
            elif job.status == "failed":
                stats.failed_jobs += 1
            elif job.status == "cancelled":
                stats.cancelled_jobs += 1

            stats.total_files_indexed += job.inserted
            stats.total_duplicates += job.duplicates
            stats.total_errors += job.errors
            stats.total_skipped += (
                job.skipped_no_media +
                job.skipped_unsupported +
                job.skipped_deleted
            )

            stats.total_indexing_time_seconds += job.duration_seconds

            if job.duration_seconds > 0:
                durations.append(job.duration_seconds)

            if job.avg_speed > 0:
                speeds.append(job.avg_speed)

        # Calculate averages
        if speeds:
            stats.avg_speed = sum(speeds) / len(speeds)
            stats.peak_speed = max(speeds)

        if durations:
            stats.avg_job_duration_seconds = sum(durations) / len(durations)
            stats.fastest_job_seconds = min(durations)
            stats.slowest_job_seconds = max(durations)

        # Channel stats
        stats.unique_channels_indexed = len(self._channel_stats)

        for channel_id, channel_data in self._channel_stats.items():
            if channel_data["files"] > stats.largest_channel_files:
                stats.largest_channel_files = channel_data["files"]
                # Try to get channel name from job stats
                for job in self._job_stats.values():
                    if job.channel_id == channel_id and job.channel_name:
                        stats.largest_channel_name = job.channel_name
                        break

        # Period stats
        for date_key, daily in self._daily_stats.items():
            date = datetime.strptime(date_key, "%Y-%m-%d").date()
            if date == today:
                stats.files_today = daily.files_indexed
            if date >= week_ago:
                stats.files_this_week += daily.files_indexed
            if date >= month_ago:
                stats.files_this_month += daily.files_indexed

        # Error analysis
        if self._errors:
            stats.most_common_error = max(
                self._errors.items(),
                key=lambda x: x[1]
            )[0]

        if stats.total_files_indexed > 0:
            stats.error_rate = stats.total_errors / (
                stats.total_files_indexed + stats.total_duplicates
            ) * 100

        return stats

    def get_recent_jobs(self, limit: int = 20) -> List[JobStatistics]:
        """Get recent job statistics."""
        jobs = sorted(
            self._job_stats.values(),
            key=lambda x: x.completed_at or datetime.min,
            reverse=True
        )
        return jobs[:limit]

    def get_job_stats(self, job_id: str) -> Optional[JobStatistics]:
        """Get statistics for a specific job."""
        return self._job_stats.get(job_id)

    def get_daily_stats(self, days: int = 7) -> List[DailyStats]:
        """Get daily statistics for the past N days."""
        now = datetime.utcnow()
        start_date = now.date() - timedelta(days=days - 1)

        result = []
        for i in range(days):
            date = start_date + timedelta(days=i)
            date_key = date.strftime("%Y-%m-%d")
            daily = self._daily_stats.get(date_key, DailyStats(date=date_key))
            result.append(daily)

        return result

    def get_channel_stats(self, channel_id: int) -> Dict[str, Any]:
        """Get statistics for a specific channel."""
        return self._channel_stats.get(channel_id, {
            "jobs": 0,
            "files": 0,
            "errors": 0,
            "total_time": 0.0
        })

    def get_top_channels(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top channels by files indexed."""
        channels = []
        for channel_id, data in self._channel_stats.items():
            # Find channel name
            channel_name = ""
            for job in self._job_stats.values():
                if job.channel_id == channel_id and job.channel_name:
                    channel_name = job.channel_name
                    break

            channels.append({
                "channel_id": channel_id,
                "channel_name": channel_name,
                "files": data["files"],
                "jobs": data["jobs"],
                "errors": data["errors"],
                "total_time_seconds": data["total_time"]
            })

        return sorted(channels, key=lambda x: x["files"], reverse=True)[:limit]

    def get_speed_distribution(self) -> Dict[str, Any]:
        """Analyze speed distribution."""
        if not self._speed_samples:
            return {
                "avg": 0,
                "min": 0,
                "max": 0,
                "median": 0,
                "p95": 0,
                "samples": 0
            }

        samples = sorted(self._speed_samples)
        n = len(samples)

        return {
            "avg": sum(samples) / n,
            "min": samples[0],
            "max": samples[-1],
            "median": samples[n // 2],
            "p95": samples[int(n * 0.95)] if n > 1 else samples[-1],
            "samples": n
        }

    def get_error_breakdown(self) -> List[Dict[str, Any]]:
        """Get breakdown of errors."""
        total = sum(self._errors.values())
        if total == 0:
            return []

        return [
            {
                "error": error,
                "count": count,
                "percentage": round(count / total * 100, 1)
            }
            for error, count in sorted(
                self._errors.items(),
                key=lambda x: x[1],
                reverse=True
            )
        ]

    # =========================================================================
    # Export
    # =========================================================================

    def export_all(self, format: str = "dict") -> Any:
        """Export all statistics."""
        data = {
            "exported_at": datetime.utcnow().isoformat(),
            "aggregate": asdict(self.get_aggregate_stats()),
            "recent_jobs": [
                asdict(job) for job in self.get_recent_jobs(10)
            ],
            "daily_stats": [
                asdict(daily) for daily in self.get_daily_stats(7)
            ],
            "top_channels": self.get_top_channels(10),
            "speed_distribution": self.get_speed_distribution(),
            "error_breakdown": self.get_error_breakdown()
        }

        if format == "json":
            return json.dumps(data, default=str, indent=2)
        return data

    # =========================================================================
    # Cleanup
    # =========================================================================

    def clear_stats(self) -> None:
        """Clear all statistics."""
        self._job_stats.clear()
        self._daily_stats.clear()
        self._channel_stats.clear()
        self._speed_samples.clear()
        self._errors.clear()

    def prune_old_stats(self, days: int = 30) -> int:
        """Remove statistics older than N days."""
        cutoff = datetime.utcnow() - timedelta(days=days)

        removed = 0
        for job_id, job in list(self._job_stats.items()):
            if job.completed_at and job.completed_at < cutoff:
                del self._job_stats[job_id]
                removed += 1

        return removed


# =============================================================================
# Global Instance
# =============================================================================

_index_stats_service: Optional[IndexStatsService] = None


def get_index_stats_service() -> IndexStatsService:
    """Get or create the global IndexStatsService instance."""
    global _index_stats_service
    if _index_stats_service is None:
        _index_stats_service = IndexStatsService()
    return _index_stats_service


def reset_index_stats_service() -> None:
    """Reset the global IndexStatsService instance."""
    global _index_stats_service
    _index_stats_service = None
