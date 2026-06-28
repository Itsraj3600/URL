import logging
import asyncio
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional
from pyrogram import Client

from core import get_event_bus, Events
from database.index_events import IndexEventDB
from database.index_history import IndexHistoryDB

logger = logging.getLogger(__name__)


@dataclass
class IndexJobContext:
    """Context for an indexing job."""
    job_id: str
    channel_id: int
    channel_title: str
    started_by: int
    total_messages: int
    job_type: str = "manual"
    telegram_message_id: Optional[int] = None
    start_time: Optional[datetime] = None
    finish_time: Optional[datetime] = None
    indexed: int = 0
    duplicates: int = 0
    skipped: int = 0
    errors: int = 0
    batches_completed: int = 0
    largest_batch: int = 0
    average_batch: float = 0.0
    mongo_speed: float = 0.0


class IndexEventLogger:
    """Event-driven index logging that integrates with the event bus."""
    
    @staticmethod
    async def on_index_start(context: IndexJobContext) -> None:
        """Handle index start event."""
        try:
            context.start_time = datetime.utcnow()
            
            # Log to database
            await IndexEventDB.log_event(
                context.job_id,
                "started",
                {
                    "channel_id": context.channel_id,
                    "channel_title": context.channel_title,
                    "total_messages": context.total_messages,
                    "started_by": context.started_by
                }
            )
            
            logger.info(f"[IndexLogger] Start event logged for {context.job_id}")
            
            # Publish to event bus for other subscribers
            event_bus = get_event_bus()
            await event_bus.publish(Events.INDEX_STARTED, {
                "job_id": context.job_id,
                "timestamp": context.start_time
            })
        except Exception as e:
            logger.error(f"[IndexLogger] Failed to log start event: {e}")
    
    @staticmethod
    async def on_index_progress(context: IndexJobContext, processed: int) -> None:
        """Handle index progress event."""
        try:
            # Log progress events periodically
            if processed % 500 == 0:
                await IndexEventDB.log_event(
                    context.job_id,
                    "progress",
                    {
                        "processed": processed,
                        "indexed": context.indexed,
                        "duplicates": context.duplicates,
                        "skipped": context.skipped,
                        "errors": context.errors
                    }
                )
                
                event_bus = get_event_bus()
                await event_bus.publish(Events.INDEX_PROGRESS, {
                    "job_id": context.job_id,
                    "processed": processed,
                    "progress_percent": (processed / context.total_messages * 100) if context.total_messages > 0 else 0
                })
        except Exception as e:
            logger.warning(f"[IndexLogger] Failed to log progress: {e}")
    
    @staticmethod
    async def on_index_pause(context: IndexJobContext) -> None:
        """Handle index pause event."""
        try:
            await IndexEventDB.log_event(
                context.job_id,
                "paused",
                {
                    "processed": context.indexed + context.duplicates + context.skipped + context.errors,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            
            event_bus = get_event_bus()
            await event_bus.publish(Events.INDEX_PAUSED, {"job_id": context.job_id})
            
            logger.info(f"[IndexLogger] Pause event logged for {context.job_id}")
        except Exception as e:
            logger.error(f"[IndexLogger] Failed to log pause event: {e}")
    
    @staticmethod
    async def on_index_resume(context: IndexJobContext, message_id: int) -> None:
        """Handle index resume event."""
        try:
            await IndexEventDB.log_event(
                context.job_id,
                "resumed",
                {
                    "message_id": message_id,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            
            event_bus = get_event_bus()
            await event_bus.publish(Events.INDEX_RESUMED, {"job_id": context.job_id})
            
            logger.info(f"[IndexLogger] Resume event logged for {context.job_id}")
        except Exception as e:
            logger.error(f"[IndexLogger] Failed to log resume event: {e}")
    
    @staticmethod
    async def on_index_complete(context: IndexJobContext) -> None:
        """Handle index completion event."""
        try:
            context.finish_time = datetime.utcnow()
            duration = int((context.finish_time - context.start_time).total_seconds()) if context.start_time else 0
            total_processed = context.indexed + context.duplicates + context.skipped + context.errors
            average_speed = total_processed / duration if duration > 0 else 0
            
            # Log completion event
            await IndexEventDB.log_event(
                context.job_id,
                "completed",
                {
                    "indexed": context.indexed,
                    "duplicates": context.duplicates,
                    "skipped": context.skipped,
                    "errors": context.errors,
                    "duration": duration,
                    "average_speed": average_speed
                }
            )
            
            # Save to history
            await IndexHistoryDB.save_job(
                job_id=context.job_id,
                channel_id=context.channel_id,
                channel_title=context.channel_title,
                started_by=context.started_by,
                job_type=context.job_type,
                indexed=context.indexed,
                duplicates=context.duplicates,
                skipped=context.skipped,
                errors=context.errors,
                duration=duration,
                average_speed=average_speed,
                mongo_speed=context.mongo_speed,
                batch_size=0,
                batches_completed=context.batches_completed,
                largest_batch=context.largest_batch,
                average_batch=context.average_batch
            )
            
            event_bus = get_event_bus()
            await event_bus.publish(Events.INDEX_COMPLETED, {
                "job_id": context.job_id,
                "indexed": context.indexed,
                "duplicates": context.duplicates,
                "skipped": context.skipped,
                "errors": context.errors,
                "duration": duration
            })
            
            logger.info(f"[IndexLogger] Completed job {context.job_id}")
        except Exception as e:
            logger.error(f"[IndexLogger] Failed to log completion: {e}")
    
    @staticmethod
    async def on_index_failed(context: IndexJobContext, error: str) -> None:
        """Handle index failure event."""
        try:
            await IndexEventDB.log_event(
                context.job_id,
                "failed",
                {
                    "error": error,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            
            event_bus = get_event_bus()
            await event_bus.publish(Events.INDEX_FAILED, {
                "job_id": context.job_id,
                "error": error
            })
            
            logger.error(f"[IndexLogger] Failed job {context.job_id}: {error}")
        except Exception as e:
            logger.error(f"[IndexLogger] Failed to log failure: {e}")
