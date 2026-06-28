"""
Index Log Service

Manages Telegram logging for indexing operations.

Features:
- Single message updates instead of spam
- Progress tracking with ETA
- Completion summaries
- Auto-index monitoring
- Clean, editable logs
"""

import logging
import asyncio
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from pyrogram import Client

from info import LOG_CHANNEL

logger = logging.getLogger(__name__)


@dataclass
class IndexStats:
    """Statistics for an indexing job."""
    job_id: str
    channel: str
    channel_title: str = ""
    started_by: int = 0
    total_messages: int = 0
    processed: int = 0
    inserted: int = 0
    duplicates: int = 0
    errors: int = 0
    progress: float = 0.0
    speed: float = 0.0
    eta: str = "Calculating..."
    duration: str = "00:00"
    average_speed: float = 0.0
    start_time: Optional[datetime] = None
    finish_time: Optional[datetime] = None


class IndexLogService:
    """Manages index logging to Telegram."""

    @staticmethod
    async def send_start(bot: Client, job_id: str, channel_title: str, started_by: int, total_messages: int) -> int:
        """Send initial index start message and return message ID."""
        try:
            text = f"""🚀 <b>Index Started</b>

🆔 <b>Job:</b> <code>{job_id}</code>
📂 <b>Channel:</b> {channel_title}
👤 <b>Started By:</b> <code>{started_by}</code>
📨 <b>Total Messages:</b> {total_messages:,}
⏱ <b>Started:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

<i>Preparing to index...</i>"""

            msg = await bot.send_message(LOG_CHANNEL, text, parse_mode="html")
            logger.info(f"[IndexLog] Started job {job_id} - message {msg.id}")
            return msg.id
        except Exception as e:
            logger.error(f"[IndexLog] Failed to send start message: {e}")
            return 0

    @staticmethod
    async def update_progress(bot: Client, message_id: int, stats: IndexStats) -> bool:
        """Update progress message with current statistics."""
        if not message_id or not LOG_CHANNEL:
            return False

        try:
            progress_bar = IndexLogService._build_progress_bar(stats.progress)

            text = f"""📊 <b>Index Progress</b>

{progress_bar}
{stats.progress:.1f}%

📥 <b>Processed:</b> {stats.processed:,}
✅ <b>Indexed:</b> {stats.inserted:,}
♻️ <b>Duplicates:</b> {stats.duplicates:,}
❌ <b>Errors:</b> {stats.errors:,}

⚡ <b>Speed:</b> {stats.speed:.1f} files/sec
⏳ <b>ETA:</b> {stats.eta}
⏱ <b>Duration:</b> {stats.duration}"""

            await bot.edit_message_text(LOG_CHANNEL, message_id, text, parse_mode="html")
            return True
        except Exception as e:
            logger.warning(f"[IndexLog] Failed to update progress message: {e}")
            return False

    @staticmethod
    async def send_complete(bot: Client, message_id: int, stats: IndexStats) -> bool:
        """Send completion message."""
        if not message_id or not LOG_CHANNEL:
            return False

        try:
            total_processed = stats.inserted + stats.duplicates + stats.errors
            success_rate = (stats.inserted / total_processed * 100) if total_processed > 0 else 0

            text = f"""✅ <b>Index Completed</b>

📂 <b>Channel:</b> {stats.channel_title}
🆔 <b>Job:</b> <code>{stats.job_id}</code>

📊 <b>Results:</b>
📥 <b>Indexed:</b> {stats.inserted:,}
♻️ <b>Duplicates:</b> {stats.duplicates:,}
❌ <b>Errors:</b> {stats.errors:,}
✅ <b>Success Rate:</b> {success_rate:.1f}%

⏱ <b>Duration:</b> {stats.duration}
⚡ <b>Average Speed:</b> {stats.average_speed:.2f} files/sec

<i>Completed at {stats.finish_time.strftime('%Y-%m-%d %H:%M:%S') if stats.finish_time else 'now'}</i>"""

            await bot.edit_message_text(LOG_CHANNEL, message_id, text, parse_mode="html")
            logger.info(f"[IndexLog] Completed job {stats.job_id}")
            return True
        except Exception as e:
            logger.error(f"[IndexLog] Failed to send complete message: {e}")
            return False

    @staticmethod
    async def send_cancelled(bot: Client, message_id: int, stats: IndexStats, reason: str = "User cancelled") -> bool:
        """Send cancellation message."""
        if not message_id or not LOG_CHANNEL:
            return False

        try:
            text = f"""⛔ <b>Index Cancelled</b>

📂 <b>Channel:</b> {stats.channel_title}
🆔 <b>Job:</b> <code>{stats.job_id}</code>
📝 <b>Reason:</b> {reason}

📊 <b>Progress:</b>
📥 <b>Processed:</b> {stats.processed:,}
✅ <b>Indexed:</b> {stats.inserted:,}
♻️ <b>Duplicates:</b> {stats.duplicates:,}
❌ <b>Errors:</b> {stats.errors:,}

⏱ <b>Duration:</b> {stats.duration}
⚡ <b>Speed:</b> {stats.average_speed:.2f} files/sec"""

            await bot.edit_message_text(LOG_CHANNEL, message_id, text, parse_mode="html")
            logger.info(f"[IndexLog] Cancelled job {stats.job_id}: {reason}")
            return True
        except Exception as e:
            logger.error(f"[IndexLog] Failed to send cancelled message: {e}")
            return False

    @staticmethod
    async def send_error(bot: Client, message_id: int, stats: IndexStats, error: str) -> bool:
        """Send error message."""
        if not message_id or not LOG_CHANNEL:
            return False

        try:
            text = f"""❌ <b>Index Failed</b>

📂 <b>Channel:</b> {stats.channel_title}
🆔 <b>Job:</b> <code>{stats.job_id}</code>
🔴 <b>Error:</b> {error}

📊 <b>Progress Before Failure:</b>
📥 <b>Processed:</b> {stats.processed:,}
✅ <b>Indexed:</b> {stats.inserted:,}
♻️ <b>Duplicates:</b> {stats.duplicates:,}

⏱ <b>Duration:</b> {stats.duration}"""

            await bot.edit_message_text(LOG_CHANNEL, message_id, text, parse_mode="html")
            logger.error(f"[IndexLog] Job {stats.job_id} failed: {error}")
            return True
        except Exception as e:
            logger.error(f"[IndexLog] Failed to send error message: {e}")
            return False

    @staticmethod
    async def send_auto_summary(bot: Client, auto_stats: Dict[str, Any]) -> int:
        """Send auto-index summary message."""
        try:
            indexed = auto_stats.get("indexed", 0)
            duplicates = auto_stats.get("duplicates", 0)
            errors = auto_stats.get("errors", 0)
            duration = auto_stats.get("duration", "00:00")

            text = f"""🤖 <b>Auto Index Summary</b>

📦 <b>Files Indexed:</b> {indexed:,}
♻️ <b>Duplicates:</b> {duplicates:,}
❌ <b>Errors:</b> {errors:,}

⏱ <b>Duration:</b> {duration}
⏰ <b>Timestamp:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""

            msg = await bot.send_message(LOG_CHANNEL, text, parse_mode="html")
            return msg.id
        except Exception as e:
            logger.error(f"[IndexLog] Failed to send auto summary: {e}")
            return 0

    @staticmethod
    def _build_progress_bar(progress: float, length: int = 20) -> str:
        """Build a visual progress bar."""
        filled = int(length * progress / 100)
        bar = "█" * filled + "░" * (length - filled)
        return f"[{bar}]"

    @staticmethod
    def _calculate_eta(processed: int, total: int, speed: float) -> str:
        """Calculate ETA in human-readable format."""
        if speed <= 0 or total <= processed:
            return "Almost done..."

        remaining = total - processed
        eta_seconds = remaining / speed
        
        hours = int(eta_seconds // 3600)
        minutes = int((eta_seconds % 3600) // 60)
        seconds = int(eta_seconds % 60)

        if hours > 0:
            return f"{hours}h {minutes}m"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"

    @staticmethod
    def _format_duration(seconds: int) -> str:
        """Format seconds into human-readable duration."""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60

        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes:02d}:{secs:02d}"


class AutoIndexLogger:
    """Manages auto-indexing progress logging."""

    def __init__(self):
        self.stats: Dict[str, Any] = {
            "indexed": 0,
            "duplicates": 0,
            "errors": 0,
            "start_time": datetime.now(),
            "last_update": datetime.now()
        }
        self.message_id = 0

    async def initialize(self, bot: Client):
        """Send initial auto-index message."""
        try:
            text = """🤖 <b>Auto Index Running</b>

<i>Monitoring channels for new media...</i>

📦 Files Indexed: 0
♻️ Duplicates: 0
❌ Errors: 0
⏱ Duration: 00:00"""

            msg = await bot.send_message(LOG_CHANNEL, text, parse_mode="html")
            self.message_id = msg.id
            logger.info(f"[AutoIndex] Initialized auto-index logger - message {msg.id}")
        except Exception as e:
            logger.error(f"[AutoIndex] Failed to initialize: {e}")

    async def update(self, bot: Client, indexed: int = 0, duplicates: int = 0, errors: int = 0):
        """Update auto-index statistics."""
        self.stats["indexed"] += indexed
        self.stats["duplicates"] += duplicates
        self.stats["errors"] += errors
        self.stats["last_update"] = datetime.now()

        # Only update every 60 seconds to avoid spam
        if (datetime.now() - datetime.fromisoformat(str(self.stats["last_update"]))).total_seconds() < 60:
            return

        duration = int((datetime.now() - self.stats["start_time"]).total_seconds())
        formatted_duration = IndexLogService._format_duration(duration)

        try:
            text = f"""🤖 <b>Auto Index Running</b>

<i>Monitoring channels for new media...</i>

📦 <b>Files Indexed:</b> {self.stats['indexed']:,}
♻️ <b>Duplicates:</b> {self.stats['duplicates']:,}
❌ <b>Errors:</b> {self.stats['errors']:,}
⏱ <b>Duration:</b> {formatted_duration}"""

            if self.message_id:
                await bot.edit_message_text(LOG_CHANNEL, self.message_id, text, parse_mode="html")
        except Exception as e:
            logger.warning(f"[AutoIndex] Failed to update: {e}")

    async def send_summary(self, bot: Client) -> bool:
        """Send final auto-index summary."""
        duration = int((datetime.now() - self.stats["start_time"]).total_seconds())
        formatted_duration = IndexLogService._format_duration(duration)

        try:
            text = f"""✅ <b>Auto Index Summary</b>

📦 <b>Total Indexed:</b> {self.stats['indexed']:,}
♻️ <b>Total Duplicates:</b> {self.stats['duplicates']:,}
❌ <b>Total Errors:</b> {self.stats['errors']:,}

⏱ <b>Session Duration:</b> {formatted_duration}
⏰ <b>Ended:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""

            if self.message_id:
                await bot.edit_message_text(LOG_CHANNEL, self.message_id, text, parse_mode="html")
                logger.info("[AutoIndex] Session completed")
            return True
        except Exception as e:
            logger.error(f"[AutoIndex] Failed to send summary: {e}")
            return False
