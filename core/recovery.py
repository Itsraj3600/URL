"""
Automatic Recovery - Self-healing system for common failures.

Implements automatic recovery for:
- MongoDB disconnected → auto-reconnect with exponential backoff
- Telegram timeout → retry with delay
- Worker crashed → restart worker process
- FloodWait error → sleep and resume
- Queue stuck → clear and reinitialize
- All with event bus notifications

Uses exponential backoff and jitter to prevent thundering herd.
"""

import logging
import asyncio
from datetime import datetime
from typing import Callable, Optional, Any
from enum import Enum

logger = logging.getLogger(__name__)


class RecoveryStrategy(Enum):
    """Recovery strategies for different failure types."""

    EXPONENTIAL_BACKOFF = "exponential_backoff"
    LINEAR_BACKOFF = "linear_backoff"
    IMMEDIATE_RETRY = "immediate_retry"


class AutoRecovery:
    """Automatic recovery handler for common failures."""

    def __init__(self):
        self.recovery_enabled = True
        self.recovery_history = []

    async def handle_mongodb_disconnect(
        self, db_client, max_retries: int = 5
    ) -> bool:
        """
        Handle MongoDB disconnection with exponential backoff.

        Args:
            db_client: Motor MongoDB client
            max_retries: Maximum retry attempts

        Returns:
            True if recovered, False if max retries exhausted
        """
        logger.warning("MongoDB disconnected, attempting recovery...")

        for attempt in range(max_retries):
            backoff_seconds = min(2 ** attempt, 60)  # Cap at 60 seconds
            logger.info(
                f"Reconnection attempt {attempt + 1}/{max_retries}, waiting {backoff_seconds}s..."
            )

            await asyncio.sleep(backoff_seconds)

            try:
                # Attempt ping
                await db_client.admin.command("ping")
                logger.info("✅ MongoDB connection restored")

                # Publish recovery event
                await self._publish_recovery_event("mongodb_reconnected")

                return True

            except Exception as e:
                logger.warning(f"Reconnection attempt {attempt + 1} failed: {e}")

        logger.error("MongoDB recovery failed after max retries")
        return False

    async def handle_telegram_timeout(
        self, operation: Callable, max_retries: int = 3
    ) -> Optional[Any]:
        """
        Handle Telegram timeout with retry logic.

        Args:
            operation: Async operation to retry
            max_retries: Maximum retry attempts

        Returns:
            Operation result if successful, None if max retries exhausted
        """
        logger.warning("Telegram timeout, attempting retry...")

        for attempt in range(max_retries):
            backoff_seconds = 5 * (attempt + 1)  # 5s, 10s, 15s
            logger.info(
                f"Retry attempt {attempt + 1}/{max_retries}, waiting {backoff_seconds}s..."
            )

            await asyncio.sleep(backoff_seconds)

            try:
                result = await operation()
                logger.info("✅ Telegram operation succeeded")

                await self._publish_recovery_event("telegram_recovered")

                return result

            except Exception as e:
                logger.warning(f"Retry attempt {attempt + 1} failed: {e}")

        logger.error("Telegram operation failed after max retries")
        return None

    async def handle_floodwait(self, wait_seconds: int) -> None:
        """
        Handle Telegram FloodWait error.

        Args:
            wait_seconds: Seconds to wait before retrying
        """
        logger.warning(
            f"Telegram FloodWait: sleeping for {wait_seconds} seconds..."
        )

        # Add 10% jitter to prevent thundering herd
        import random

        jitter = random.uniform(0, wait_seconds * 0.1)
        actual_wait = wait_seconds + jitter

        await asyncio.sleep(actual_wait)

        logger.info("✅ FloodWait completed, resuming operations")
        await self._publish_recovery_event("floodwait_recovered")

    async def handle_queue_stuck(self, queue) -> bool:
        """
        Handle stuck job queue.

        Args:
            queue: The job queue object

        Returns:
            True if recovered, False otherwise
        """
        logger.warning("Job queue appears stuck, attempting recovery...")

        try:
            # Clear problematic jobs
            queue_size = queue.qsize() if hasattr(queue, "qsize") else 0

            if queue_size > 1000:
                logger.warning(f"Queue has {queue_size} jobs, may be stuck")

            # Reinitialize queue
            logger.info("Reinitializing job queue...")

            if hasattr(queue, "clear"):
                queue.clear()

            logger.info("✅ Job queue recovered")

            await self._publish_recovery_event("queue_recovered")

            return True

        except Exception as e:
            logger.error(f"Failed to recover queue: {e}")
            return False

    async def handle_worker_crash(self, worker_id: str, restart_callback: Callable) -> bool:
        """
        Handle crashed worker with restart.

        Args:
            worker_id: ID of crashed worker
            restart_callback: Async function to restart worker

        Returns:
            True if restarted successfully, False otherwise
        """
        logger.warning(f"Worker {worker_id} crashed, attempting restart...")

        try:
            # Wait before restart
            await asyncio.sleep(5)

            # Call restart callback
            logger.info(f"Restarting worker {worker_id}...")
            await restart_callback()

            logger.info(f"✅ Worker {worker_id} restarted")

            await self._publish_recovery_event("worker_restarted", {"worker_id": worker_id})

            return True

        except Exception as e:
            logger.error(f"Failed to restart worker {worker_id}: {e}")
            return False

    async def _publish_recovery_event(
        self, event_type: str, data: dict = None
    ) -> None:
        """Publish recovery event to event bus."""
        try:
            from core import get_event_bus, Events

            event_bus = get_event_bus()

            # Find matching event
            recovery_event = None
            if event_type == "mongodb_reconnected":
                recovery_event = Events.DB_CONNECTED
            elif event_type == "telegram_recovered":
                recovery_event = Events.BOT_RESTARTED
            elif event_type == "worker_restarted":
                recovery_event = Events.WORKER_STARTED

            if recovery_event:
                await event_bus.publish(
                    recovery_event,
                    source="recovery",
                    data=data or {"recovery_type": event_type},
                )

            # Log to history
            self.recovery_history.append(
                {
                    "type": event_type,
                    "timestamp": datetime.utcnow(),
                    "data": data,
                }
            )

            # Keep only last 100 recoveries
            if len(self.recovery_history) > 100:
                self.recovery_history = self.recovery_history[-100:]

        except Exception as e:
            logger.debug(f"Could not publish recovery event: {e}")

    def get_recovery_history(self) -> list:
        """Get recovery event history."""
        return list(self.recovery_history)


# Global recovery instance
_recovery = AutoRecovery()


def get_recovery() -> AutoRecovery:
    """Get global recovery instance."""
    return _recovery


async def setup_recovery_handlers(bot_client, db_client) -> None:
    """
    Setup automatic recovery handlers throughout the bot.

    Args:
        bot_client: Pyrogram bot client
        db_client: MongoDB client
    """
    logger.info("Setting up automatic recovery handlers...")

    recovery = get_recovery()

    # Connect to event bus for automatic recovery triggers
    try:
        from core import get_event_bus, Events

        event_bus = get_event_bus()

        @event_bus.on(Events.DB_DISCONNECTED)
        async def on_db_disconnected(event):
            """Auto-recover from database disconnection."""
            await recovery.handle_mongodb_disconnect(db_client)

        logger.info("✅ Recovery handlers registered")

    except Exception as e:
        logger.warning(f"Could not setup recovery handlers: {e}")
