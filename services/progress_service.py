"""
Progress Service

Tracks and reports progress for indexing operations.

Features:
- Real-time progress tracking
- Speed calculations
- ETA estimation
- Progress updates to Telegram
- Progress persistence
"""

import logging
import time
import math
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Callable, Any
from enum import Enum

logger = logging.getLogger(__name__)


class ProgressStage(str, Enum):
    INITIALIZING = "initializing"
    READING = "reading"
    PROCESSING = "processing"
    WRITING = "writing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"


@dataclass
class ProgressState:
    """Current progress state."""
    job_id: str
    channel_name: str = ""

    # Counts
    total_messages: int = 0
    processed: int = 0
    inserted: int = 0
    duplicates: int = 0
    errors: int = 0
    skipped: int = 0

    # Speed
    files_per_second: float = 0.0
    messages_per_second: float = 0.0
    peak_speed: float = 0.0
    avg_speed: float = 0.0

    # ETA
    eta_seconds: int = 0
    eta_human: str = ""

    # Progress
    percent_complete: float = 0.0
    progress_bar: str = ""

    # Timing
    elapsed_seconds: int = 0
    elapsed_human: str = ""

    # Stage
    stage: ProgressStage = ProgressStage.INITIALIZING
    current_batch: int = 0
    batch_size: int = 500

    # Telegram message
    progress_message_id: Optional[int] = None
    last_updated: Optional[datetime] = None


class ProgressService:
    """
    Service for tracking and reporting index progress.

    Usage:
        progress = get_progress_service()

        # Start tracking
        state = progress.start(job_id="abc123", total_messages=10000)

        # Update
        progress.update(
            job_id="abc123",
            processed=500,
            inserted=450,
            duplicates=50
        )

        # Get formatted message
        msg = progress.format_message(job_id)
    """

    def __init__(self, update_interval: int = 30):
        self.update_interval = update_interval
        self._states: dict = {}
        self._start_times: dict = {}
        self._last_updates: dict = {}
        self._speed_history: dict = {}  # job_id -> [(time, count)]

    def start(
        self,
        job_id: str,
        total_messages: int = 0,
        channel_name: str = "",
        batch_size: int = 500
    ) -> ProgressState:
        """Start tracking progress for a job."""
        state = ProgressState(
            job_id=job_id,
            total_messages=total_messages,
            channel_name=channel_name,
            batch_size=batch_size,
            stage=ProgressStage.INITIALIZING
        )

        self._states[job_id] = state
        self._start_times[job_id] = time.monotonic()
        self._last_updates[job_id] = 0
        self._speed_history[job_id] = []

        return state

    def update(
        self,
        job_id: str,
        processed: Optional[int] = None,
        inserted: Optional[int] = None,
        duplicates: Optional[int] = None,
        errors: Optional[int] = None,
        skipped: Optional[int] = None,
        total_messages: Optional[int] = None,
        stage: Optional[ProgressStage] = None,
        current_batch: Optional[int] = None
    ) -> Optional[ProgressState]:
        """Update progress state."""
        state = self._states.get(job_id)
        if not state:
            return None

        now = time.monotonic()

        # Update counts
        if processed is not None:
            state.processed = processed
        if inserted is not None:
            state.inserted = inserted
        if duplicates is not None:
            state.duplicates = duplicates
        if errors is not None:
            state.errors = errors
        if skipped is not None:
            state.skipped = skipped
        if total_messages is not None:
            state.total_messages = total_messages
        if stage is not None:
            state.stage = stage
        if current_batch is not None:
            state.current_batch = current_batch

        # Calculate elapsed time
        start_time = self._start_times.get(job_id, now)
        elapsed = now - start_time
        state.elapsed_seconds = int(elapsed)
        state.elapsed_human = self._format_time(elapsed)

        # Calculate speed
        if elapsed > 0:
            state.files_per_second = state.inserted / elapsed
            state.messages_per_second = state.processed / elapsed

            if state.files_per_second > state.peak_speed:
                state.peak_speed = state.files_per_second

            # Track speed history for average
            history = self._speed_history.get(job_id, [])
            history.append((now, state.inserted))
            # Keep last 60 samples (1 minute at 1s intervals)
            if len(history) > 60:
                history = history[-60:]
            self._speed_history[job_id] = history

            # Calculate average from history
            if len(history) >= 2:
                time_diff = history[-1][0] - history[0][0]
                count_diff = history[-1][1] - history[0][1]
                if time_diff > 0:
                    state.avg_speed = count_diff / time_diff

        # Calculate ETA
        if state.avg_speed > 0 and state.total_messages > 0:
            remaining = state.total_messages - state.processed
            eta = remaining / state.avg_speed
            state.eta_seconds = int(eta)
            state.eta_human = self._format_time(eta)

        # Calculate percent
        if state.total_messages > 0:
            state.percent_complete = (state.processed / state.total_messages) * 100

        # Build progress bar
        state.progress_bar = self._build_progress_bar(state.percent_complete)

        state.last_updated = datetime.utcnow()

        return state

    def should_update(self, job_id: str) -> bool:
        """Check if enough time has passed for an update."""
        now = time.monotonic()
        last = self._last_updates.get(job_id, 0)
        if now - last >= self.update_interval:
            self._last_updates[job_id] = now
            return True
        return False

    def get_state(self, job_id: str) -> Optional[ProgressState]:
        """Get current progress state."""
        return self._states.get(job_id)

    def complete(self, job_id: str) -> Optional[ProgressState]:
        """Mark progress as completed."""
        state = self._states.get(job_id)
        if state:
            state.stage = ProgressStage.COMPLETED
            state.percent_complete = 100.0
            state.progress_bar = self._build_progress_bar(100)
            self._cleanup(job_id)
        return state

    def cancel(self, job_id: str) -> Optional[ProgressState]:
        """Mark progress as cancelled."""
        state = self._states.get(job_id)
        if state:
            state.stage = ProgressStage.CANCELLED
            self._cleanup(job_id)
        return state

    def fail(self, job_id: str) -> Optional[ProgressState]:
        """Mark progress as failed."""
        state = self._states.get(job_id)
        if state:
            state.stage = ProgressStage.FAILED
            self._cleanup(job_id)
        return state

    def format_message(self, job_id: str) -> str:
        """Format progress as Telegram message."""
        state = self._states.get(job_id)
        if not state:
            return "No progress data"

        # Build message based on stage
        if state.stage == ProgressStage.COMPLETED:
            return self._format_complete(state)
        elif state.stage == ProgressStage.CANCELLED:
            return self._format_cancelled(state)
        elif state.stage == ProgressStage.FAILED:
            return self._format_failed(state)
        else:
            return self._format_running(state)

    def _format_running(self, state: ProgressState) -> str:
        """Format running progress."""
        lines = [
            f"🚀 Indexing: {state.channel_name or state.job_id}",
            "",
            f"{state.progress_bar} {state.percent_complete:.1f}%",
            "",
            f"📊 **Stats:**",
            f"  • Processed: `{state.processed:,}`",
            f"  • Inserted: `{state.inserted:,}`",
            f"  • Duplicates: `{state.duplicates:,}`",
            f"  • Errors: `{state.errors:,}`",
            "",
            f"⚡ **Speed:** `{state.files_per_second:.1f} files/sec`",
            f"⏱ **Elapsed:** `{state.elapsed_human}`",
            f"🕐 **ETA:** `{state.eta_human or 'calculating...'}`",
        ]

        if state.current_batch > 0:
            lines.append(f"📦 **Batch:** `{state.current_batch}`")

        return "\n".join(lines)

    def _format_complete(self, state: ProgressState) -> str:
        """Format completion message."""
        lines = [
            "✅ **Index Complete**",
            "",
            f"📁 **Channel:** {state.channel_name or state.job_id}",
            "",
            f"📊 **Results:**",
            f"  • Total Inserted: `{state.inserted:,}`",
            f"  • Duplicates Skipped: `{state.duplicates:,}`",
            f"  • Errors: `{state.errors:,}`",
            f"  • Skipped: `{state.skipped:,}`",
            "",
            f"⏱ **Time:** `{state.elapsed_human}`",
            f"⚡ **Avg Speed:** `{state.avg_speed:.1f} files/sec`",
        ]

        if state.peak_speed > 0:
            lines.append(f"🚀 **Peak Speed:** `{state.peak_speed:.1f} files/sec`")

        return "\n".join(lines)

    def _format_cancelled(self, state: ProgressState) -> str:
        """Format cancelled message."""
        lines = [
            "⚠️ **Index Cancelled**",
            "",
            f"📁 **Channel:** {state.channel_name or state.job_id}",
            "",
            f"📊 **Partial Results:**",
            f"  • Inserted: `{state.inserted:,}`",
            f"  • Duplicates: `{state.duplicates:,}`",
            "",
            f"⏱ **Time:** `{state.elapsed_human}`",
        ]
        return "\n".join(lines)

    def _format_failed(self, state: ProgressState) -> str:
        """Format failed message."""
        lines = [
            "❌ **Index Failed**",
            "",
            f"📁 **Channel:** {state.channel_name or state.job_id}",
            "",
            f"📊 **Partial Results:**",
            f"  • Processed: `{state.processed:,}`",
            f"  • Inserted: `{state.inserted:,}`",
            "",
            f"⏱ **Time:** `{state.elapsed_human}`",
        ]
        return "\n".join(lines)

    def _build_progress_bar(self, percent: float, width: int = 20) -> str:
        """Build Unicode progress bar."""
        filled = int((percent / 100) * width)
        empty = width - filled

        # Use block characters
        bar = "█" * filled + "░" * empty

        # Add stages
        stages = ["", "▏", "▎", "▍", "▌", "▋", "▊", "▉", "█"]

        return f"`[{bar}]`"

    def _format_time(self, seconds: float) -> str:
        """Format seconds to human readable."""
        if seconds < 0:
            return "N/A"

        seconds = int(seconds)

        if seconds < 60:
            return f"{seconds}s"

        minutes = seconds // 60
        seconds = seconds % 60

        if minutes < 60:
            return f"{minutes}m {seconds}s"

        hours = minutes // 60
        minutes = minutes % 60

        return f"{hours}h {minutes}m"

    def _cleanup(self, job_id: str) -> None:
        """Cleanup tracking data for completed job."""
        self._speed_history.pop(job_id, None)
        self._last_updates.pop(job_id, None)


# =============================================================================
# Global Instance
# =============================================================================

_progress_service: Optional[ProgressService] = None


def get_progress_service() -> ProgressService:
    """Get or create the global ProgressService instance."""
    global _progress_service
    if _progress_service is None:
        _progress_service = ProgressService()
    return _progress_service


def reset_progress_service() -> None:
    """Reset the global ProgressService instance."""
    global _progress_service
    _progress_service = None
