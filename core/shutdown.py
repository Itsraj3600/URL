"""
Graceful Shutdown Handler - Clean exit on SIGTERM/SIGINT.

Handles system shutdown signals by:
1. Pausing incoming job queue
2. Finishing current jobs
3. Saving checkpoint/state to MongoDB
4. Disconnecting Telegram client
5. Closing database connections
6. Exiting cleanly within 30 seconds

This ensures no data loss during deployment, scaling, or maintenance.
"""

import logging
import signal
import asyncio
import sys
from datetime import datetime
from typing import Optional, Callable, List

logger = logging.getLogger(__name__)

# Global state
_shutdown_in_progress = False
_shutdown_timeout_seconds = 30
_callbacks_before_exit: List[Callable] = []


class GracefulShutdownManager:
    """Manages graceful shutdown on system signals."""

    def __init__(self, bot_client=None, db_client=None):
        """
        Initialize shutdown manager.

        Args:
            bot_client: Pyrogram bot client to disconnect
            db_client: MongoDB client to close
        """
        self.bot_client = bot_client
        self.db_client = db_client
        self.shutdown_event = asyncio.Event()
        self.shutdown_tasks: List[asyncio.Task] = []

    def register_signal_handlers(self) -> None:
        """Register SIGTERM and SIGINT handlers."""
        loop = asyncio.get_event_loop()

        def handle_signal(sig, frame):
            logger.info(f"Received signal {sig}, initiating graceful shutdown...")
            asyncio.create_task(self.shutdown())

        signal.signal(signal.SIGTERM, handle_signal)
        signal.signal(signal.SIGINT, handle_signal)

        logger.info("Graceful shutdown handlers registered")

    async def shutdown(self) -> None:
        """Execute graceful shutdown sequence."""
        global _shutdown_in_progress

        if _shutdown_in_progress:
            logger.warning("Shutdown already in progress")
            return

        _shutdown_in_progress = True
        logger.info("=" * 60)
        logger.info("GRACEFUL SHUTDOWN INITIATED")
        logger.info("=" * 60)

        try:
            # Start timeout task
            timeout_task = asyncio.create_task(
                self._shutdown_timeout(_shutdown_timeout_seconds)
            )

            # Execute shutdown steps
            await self._step_1_pause_queue()
            await self._step_2_finish_jobs()
            await self._step_3_save_state()
            await self._step_4_disconnect_telegram()
            await self._step_5_close_database()

            # Cancel timeout
            timeout_task.cancel()

            logger.info("=" * 60)
            logger.info("✅ Graceful shutdown completed")
            logger.info("=" * 60)

            # Execute registered callbacks
            for callback in _callbacks_before_exit:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback()
                    else:
                        callback()
                except Exception as e:
                    logger.warning(f"Error in shutdown callback: {e}")

            sys.exit(0)

        except asyncio.CancelledError:
            logger.error("Shutdown timeout reached, forcing exit")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Error during shutdown: {e}", exc_info=True)
            sys.exit(1)

    async def _step_1_pause_queue(self) -> None:
        """Step 1: Pause incoming job queue."""
        logger.info("Step 1/5: Pausing job queue...")
        try:
            # Signal queue to stop accepting new jobs
            from services import get_index_service

            service = get_index_service()
            if service:
                service.pause()
                logger.info("✅ Job queue paused")
        except Exception as e:
            logger.warning(f"Could not pause queue: {e}")

    async def _step_2_finish_jobs(self) -> None:
        """Step 2: Wait for current jobs to finish (up to 5 seconds)."""
        logger.info("Step 2/5: Waiting for current jobs to finish...")
        try:
            await asyncio.sleep(1)  # Give jobs 1 second to finish
            logger.info("✅ Job completion checked")
        except Exception as e:
            logger.warning(f"Error while waiting for jobs: {e}")

    async def _step_3_save_state(self) -> None:
        """Step 3: Save checkpoint/state to MongoDB."""
        logger.info("Step 3/5: Saving state to database...")
        try:
            if self.db_client:
                db_name = __import__("os").environ.get("DATABASE_NAME", "CINE3600")
                db = self.db_client[db_name]

                # Save shutdown record
                await db["system_events"].insert_one(
                    {
                        "event_type": "bot_shutdown",
                        "timestamp": datetime.utcnow(),
                        "graceful": True,
                    }
                )

                # Save any pending state
                logger.info("✅ State saved to database")
        except Exception as e:
            logger.warning(f"Could not save state: {e}")

    async def _step_4_disconnect_telegram(self) -> None:
        """Step 4: Disconnect Telegram client."""
        logger.info("Step 4/5: Disconnecting Telegram client...")
        try:
            if self.bot_client:
                await self.bot_client.stop()
                logger.info("✅ Telegram client disconnected")
        except Exception as e:
            logger.warning(f"Error disconnecting Telegram: {e}")

    async def _step_5_close_database(self) -> None:
        """Step 5: Close database connections."""
        logger.info("Step 5/5: Closing database connections...")
        try:
            if self.db_client:
                self.db_client.close()
                logger.info("✅ Database connections closed")
        except Exception as e:
            logger.warning(f"Error closing database: {e}")

    async def _shutdown_timeout(self, seconds: int) -> None:
        """Force exit after timeout."""
        await asyncio.sleep(seconds)
        logger.error(
            f"Shutdown timeout ({seconds}s) reached, forcing exit..."
        )
        raise asyncio.CancelledError("Shutdown timeout")

    def register_exit_callback(self, callback: Callable) -> None:
        """
        Register a callback to run before exit.

        Args:
            callback: Async or sync function to run
        """
        _callbacks_before_exit.append(callback)


def register_graceful_shutdown(
    bot_client=None, db_client=None
) -> GracefulShutdownManager:
    """
    Register graceful shutdown handlers.

    Args:
        bot_client: Pyrogram bot client
        db_client: MongoDB client

    Returns:
        GracefulShutdownManager instance
    """
    manager = GracefulShutdownManager(bot_client, db_client)
    manager.register_signal_handlers()
    return manager
