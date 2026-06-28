import logging
import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from pyrogram import Client

from info import LOG_CHANNEL

logger = logging.getLogger(__name__)


@dataclass
class IndexStats:
    """Enhanced statistics for an indexing job."""
    job_id: str
    channel: str
    channel_title: str = ""
    started_by: int = 0
    total_messages: int = 0
    processed: int = 0
    indexed: int = 0
    duplicates: int = 0
    skipped: int = 0
    errors: int = 0
    progress: float = 0.0
    speed: float = 0.0
    mongo_speed: float = 0.0
    eta: str = "Calculating..."
    duration: str = "00:00"
    average_speed: float = 0.0
    start_time: Optional[datetime] = None
    finish_time: Optional[datetime] = None
    last_update: Optional[datetime] = None
    batch_size: int = 0
    batches_completed: int = 0
    largest_batch: int = 0
    average_batch: float = 0.0
    last_message_id: int = 0
    resume_message_id: Optional[int] = None
    

class IndexLogService:
    """Enhanced index logging with event-driven architecture."""
    
    @staticmethod
    async def send_start(
        bot: Client,
        job_id: str,
        channel_title: str,
        started_by: int,
        total_messages: int
    ) -> int:
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
    async def send_resume(
        bot: Client,
        job_id: str,
        recovered_message_id: int,
        channel_title: str
    ) -> int:
        """Log resume event after bot restart."""
        try:
            text = f"""♻️ <b>Index Resumed</b>

🆔 <b>Job:</b> <code>{job_id}</code>
📂 <b>Channel:</b> {channel_title}
📍 <b>Recovered Job:</b> <code>{job_id}</code>
📨 <b>Starting From Message:</b> {recovered_message_id}
⏱ <b>Resumed:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

<i>Continuing indexing...</i>"""
            
            msg = await bot.send_message(LOG_CHANNEL, text, parse_mode="html")
            logger.info(f"[IndexLog] Resumed job {job_id} - message {msg.id}")
            return msg.id
        except Exception as e:
            logger.error(f"[IndexLog] Failed to send resume message: {e}")
            return 0
    
    @staticmethod
    def should_update(stats: IndexStats, update_interval: int = 30) -> bool:
        """Check if update should happen based on items or time."""
        if not stats.last_update:
            return True
        
        # Update if processed 500 items
        if stats.processed % 500 == 0 and stats.processed > 0:
            return True
        
        # Update if time interval passed
        time_diff = (datetime.utcnow() - stats.last_update).total_seconds()
        if time_diff >= update_interval:
            return True
        
        return False
    
    @staticmethod
    async def update_progress(
        bot: Client,
        message_id: int,
        stats: IndexStats
    ) -> bool:
        """Update progress message with enhanced statistics."""
        if not message_id or not LOG_CHANNEL:
            return False
        
        if not IndexLogService.should_update(stats):
            return True
        
        try:
            progress_bar = IndexLogService._build_progress_bar(stats.progress)
            
            text = f"""📊 <b>Index Progress</b>

{progress_bar}
{stats.progress:.1f}%

📥 <b>New Messages:</b> {stats.processed:,}
✅ <b>Indexed:</b> {stats.indexed:,}
♻️ <b>Duplicates:</b> {stats.duplicates:,}
⏭️ <b>Skipped:</b> {stats.skipped:,}
❌ <b>Errors:</b> {stats.errors:,}

⚡ <b>Speed:</b> {stats.speed:.1f} files/sec
📊 <b>Mongo Speed:</b> {stats.mongo_speed:.1f} writes/sec
⏳ <b>ETA:</b> {stats.eta}
⏱ <b>Duration:</b> {stats.duration}

📦 <b>Batch Info:</b>
   Completed: {stats.batches_completed} | Avg Size: {stats.average_batch:.0f} | Max: {stats.largest_batch}"""
            
            await bot.edit_message_text(LOG_CHANNEL, message_id, text, parse_mode="html")
            stats.last_update = datetime.utcnow()
            return True
        except Exception as e:
            logger.warning(f"[IndexLog] Failed to update progress: {e}")
            return False
    
    @staticmethod
    async def send_completion(
        bot: Client,
        message_id: int,
        stats: IndexStats
    ) -> bool:
        """Send completion summary with detailed breakdown."""
        if not message_id or not LOG_CHANNEL:
            return False
        
        try:
            duration = stats.finish_time - stats.start_time if stats.start_time and stats.finish_time else timedelta()
            
            text = f"""✅ <b>Index Completed</b>

🆔 <b>Job:</b> <code>{stats.job_id}</code>

📊 <b>Summary:</b>
   <b>New Messages:</b> {stats.processed:,}
   <b>Indexed:</b> {stats.indexed:,}
   <b>Duplicates:</b> {stats.duplicates:,}
   <b>Skipped:</b> {stats.skipped:,}
   <b>Errors:</b> {stats.errors:,}

⚡ <b>Performance:</b>
   <b>Avg Speed:</b> {stats.average_speed:.2f} files/sec
   <b>Mongo Speed:</b> {stats.mongo_speed:.2f} writes/sec
   <b>Duration:</b> {str(duration).split('.')[0]}
   <b>Batches:</b> {stats.batches_completed} (avg: {stats.average_batch:.0f})

📈 <b>Success Rate:</b> {(stats.indexed / stats.processed * 100):.1f}% if stats.processed > 0 else 0%

⏱ <b>Completed:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
            
            await bot.edit_message_text(LOG_CHANNEL, message_id, text, parse_mode="html")
            logger.info(f"[IndexLog] Completed job {stats.job_id}")
            return True
        except Exception as e:
            logger.error(f"[IndexLog] Failed to send completion: {e}")
            return False
    
    @staticmethod
    def _build_progress_bar(progress: float, length: int = 20) -> str:
        """Build a visual progress bar."""
        filled = int(length * progress / 100)
        bar = "█" * filled + "░" * (length - filled)
        return f"[{bar}]"
