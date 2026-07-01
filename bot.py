"""
Worker Process (Telegram Bot)

This is the ONLY process that connects to Telegram.
It handles:
- Telegram updates
- Message handlers
- Bot commands
- Indexing channels
- Background workers

Architecture:
    Worker (bot.py)          Web (web.py)
         ↓                        ↓
    Telegram API ←  ONLY  →   HTTP Dashboard
         ↓                        ↓
    Shared State ←--------→ Shared State
         ↓
    MongoDB / Supabase

The worker publishes bot status, indexing progress, and statistics
to shared state, which the web process reads for the dashboard.
"""

import logging
import logging.config
from pyrogram import __version__, idle
from pyrogram.raw.all import layer
from os import environ
from datetime import date, datetime
import pytz
import asyncio

from database.client import connect_all, PRIMARY
from database.utils import ensure_all_indexes
from database.schema import setup_production_schema
from database.users_chats_db import db
from info import *
from utils import temp
from Script import script
from util.keepalive import ping_server
from cinebot import Cine3600Bot
from cinebot.clients import initialize_clients
from services.shared_state import initialize_shared_state, get_shared_state
from core import get_event_bus, Events
from core.startup import validate_startup
from core.shutdown import register_graceful_shutdown
from workers.heartbeat import WorkerHeartbeat


# Configure logging
logging.config.fileConfig('logging.conf')
logging.getLogger().setLevel(logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.getLogger("imdbpy").setLevel(logging.ERROR)
logging.getLogger("aiohttp").setLevel(logging.ERROR)
logging.getLogger("aiohttp.web").setLevel(logging.ERROR)

logger = logging.getLogger(__name__)


async def Cine_start():
    """
    Main startup function for the Telegram bot worker.

    This function:
    1. Validates startup configuration
    2. Connects to Telegram
    3. Initializes databases
    4. Sets up shared state for dashboard
    5. Starts workers and monitoring
    6. Enters idle loop
    """
    print('\n' + '=' * 50)
    print('🎬 Initializing CINE3600 Bot Worker')
    print('=' * 50)

    # =================================================================
    # Step 0: Validate Startup Configuration
    # =================================================================
    logger.info("Step 0/8: Validating startup configuration...")

    startup_ok = await validate_startup()

    if not startup_ok:
        logger.error("❌ Startup validation failed.")
        raise RuntimeError("Startup validation failed")

    # =================================================================
    # Step 1: Initialize Shared State
    # =================================================================
    logger.info("Step 1/8: Initializing shared state...")
    shared_state = await initialize_shared_state()

    # Mark bot as starting
    await shared_state.set_bot_status(
        status="starting",
        username="",
        user_id=0
    )

    # =================================================================
    # Step 2: Start Telegram Bot
    # =================================================================
    logger.info("Step 2/8: Starting Telegram Bot...")
    await Cine3600Bot.start()

    # Get bot info
    bot_info = await Cine3600Bot.get_me()
    Cine3600Bot.username = bot_info.username
    temp.ME = bot_info.id
    temp.U_NAME = bot_info.username
    temp.B_NAME = bot_info.first_name

    logger.info(f"Connected as @{bot_info.username} (ID: {bot_info.id})")

    # Update shared state with bot status
    await shared_state.set_bot_status(
        status="online",
        username=bot_info.username,
        user_id=bot_info.id,
        start_time=datetime.utcnow()
    )

    # =================================================================
    # Step 3: Initialize Clients
    # =================================================================
    logger.info("Step 3/8: Initializing clients...")
    await initialize_clients()

    # =================================================================
    # Step 4: Connect to Databases
    # =================================================================
    logger.info("Step 4/8: Connecting to databases...")
    alive_nodes = await connect_all()

    database_ready = bool(alive_nodes)
    if not database_ready:
        logger.warning(
            "No MongoDB nodes are currently reachable. Continuing in degraded mode."
        )

    if PRIMARY.client is None:
        raise RuntimeError("Primary MongoDB client was not initialized")

    if database_ready:
        try:
            await setup_production_schema(PRIMARY.client)
        except Exception as e:
            logger.exception(f"Schema setup failed: {e}")
            raise

    # Keep Heroku server alive (if on Heroku)
    if ON_HEROKU:
        asyncio.create_task(ping_server())

    # =================================================================
    # Step 5: Load Banned Users and Verify Indexes
    # =================================================================
    if database_ready:
        logger.info("Step 5/8: Loading banned users...")
        b_users, b_chats = await db.get_banned()
        temp.BANNED_USERS = b_users
        temp.BANNED_CHATS = b_chats

        logger.info("Step 5/8: Verifying database indexes...")
        await ensure_all_indexes()

        logger.info("Step 5/8: Initializing index history...")
        from database.index_history import IndexHistoryDB
        await IndexHistoryDB.initialize()

        logger.info("✅ Database Ready")
    else:
        logger.warning("Skipping database bootstrap tasks until a node becomes reachable.")

    # =================================================================
    # Step 6: Start Worker Heartbeat
    # =================================================================
    logger.info("Step 6/8: Starting worker heartbeat monitoring...")
    heartbeat = WorkerHeartbeat("main", PRIMARY.client)
    heartbeat_task = asyncio.create_task(heartbeat.start())
    temp.HEARTBEAT = heartbeat

    # =================================================================
    # Step 7: Start Background Workers
    # =================================================================
    logger.info("Step 7/8: Starting background workers...")
    if database_ready:
        await start_background_workers()
    else:
        logger.warning("Skipping background worker startup until database connectivity is restored.")

    # =================================================================
    # Step 8: Setup Event Handlers & Graceful Shutdown
    # =================================================================
    logger.info("Step 8/8: Setting up event handlers and shutdown handlers...")
    setup_event_handlers()

    # Register graceful shutdown handlers
    register_graceful_shutdown(Cine3600Bot, PRIMARY.client)

    # =================================================================
    # Notify Success
    # =================================================================
    logger.info(f"{bot_info.first_name} with Pyrogram v{__version__} (Layer {layer}) started on @{bot_info.username}.")
    logger.info(LOG_STR)
    logger.info(script.LOGO)

    # Time logging
    TIMEZONE = environ.get("TIMEZONE", "UTC")
    tz = pytz.timezone(TIMEZONE)
    today = date.today()
    now = datetime.now(tz)
    time = now.strftime("%H:%M:%S %p")

    # Send startup message
    try:
        if LOG_CHANNEL:
            await Cine3600Bot.send_message(
                chat_id=LOG_CHANNEL,
                text=script.RESTART_TXT.format(today, time)
            )
    except Exception as e:
        logger.warning(f"Unable to send startup message: {e}")

    # =================================================================
    # Enter Idle Loop
    # =================================================================
    print('\n' + '=' * 50)
    print('✅ CINE3600 Bot is Online')
    print('📢 Waiting for messages...')
    print('=' * 50)

    logger.info("Bot started successfully. Entering idle loop...")

    # Start periodic dashboard heartbeat
    heartbeat_loop_task = asyncio.create_task(heartbeat_loop())

    # Publish startup event
    event_bus = get_event_bus()
    if database_ready:
        await event_bus.publish(
            Events.DB_CONNECTED,
            source="bot.py"
        )

    # Keep the bot running
    try:
        await idle()
    finally:
        temp.STOPPING = True

        heartbeat_task.cancel()

        try:
            await heartbeat_task
        except asyncio.CancelledError:
            pass

        heartbeat_loop_task.cancel()

        try:
            await heartbeat_loop_task
        except asyncio.CancelledError:
            pass

        logger.info("Heartbeat stopped")


async def start_background_workers():
    """Start background workers for indexing, stats, etc."""
    try:
        # Load pending index jobs
        from services import get_index_service
        index_service = get_index_service()
        await index_service.load_pending_jobs()
        logger.info("✅ Index service loaded")

    except Exception as e:
        logger.warning(f"Failed to start some workers: {e}")


def setup_event_handlers():
    """Setup event bus handlers for updating shared state."""
    event_bus = get_event_bus()
    shared_state = get_shared_state()

    @event_bus.on(Events.INDEX_STARTED)
    async def on_index_started(event):
        """Handle index start - update shared state."""
        await shared_state.set_index_status({
            "active_job_id": event.data.get("job_id"),
            "channel_id": event.data.get("channel_id"),
            "status": "running"
        })

    @event_bus.on(Events.INDEX_PROGRESS)
    async def on_index_progress(event):
        """Handle index progress updates."""
        await shared_state.set_index_status(event.data)

    @event_bus.on(Events.INDEX_COMPLETED)
    async def on_index_completed(event):
        """Handle index completion."""
        await shared_state.set_index_status({
            "active_job_id": None,
            "progress_percent": 100,
            "status": "completed"
        })

    logger.debug("Event handlers configured")


async def heartbeat_loop():
    """Periodic heartbeat to update shared state."""
    shared_state = get_shared_state()

    if shared_state is None:
        return

    while not getattr(temp, "STOPPING", False):
        try:
            await shared_state.update_bot_heartbeat()
            await asyncio.sleep(30)  # Every 30 seconds
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Heartbeat error: {e}")
            await asyncio.sleep(10)


if __name__ == '__main__':
    try:
        asyncio.run(Cine_start())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user.")
    except Exception:
        logger.exception("Fatal startup error")