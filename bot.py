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
from datetime import date, datetime
import pytz
import asyncio

from database.client import connect_all
from database.utils import ensure_all_indexes
from database.users_chats_db import db
from info import *
from utils import temp
from Script import script
from util.keepalive import ping_server
from cinebot import Cine3600Bot
from cinebot.clients import initialize_clients
from services.shared_state import initialize_shared_state, get_shared_state
from core import get_event_bus, Events


# Configure logging
logging.config.fileConfig('logging.conf')
logging.getLogger().setLevel(logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.getLogger("imdbpy").setLevel(logging.ERROR)
logging.getLogger("aiohttp").setLevel(logging.ERROR)
logging.getLogger("aiohttp.web").setLevel(logging.ERROR)

logger = logging.getLogger(__name__)

# Create asyncio event loop
loop = asyncio.get_event_loop()


async def Cine_start():
    """
    Main startup function for the Telegram bot worker.

    This function:
    1. Connects to Telegram
    2. Initializes databases
    3. Sets up shared state for dashboard
    4. Starts workers
    5. Enters idle loop
    """
    print('\n' + '=' * 50)
    print('🎬 Initializing CINE3600 Bot Worker')
    print('=' * 50)

    # =================================================================
    # Step 1: Initialize Shared State
    # =================================================================
    logger.info("Step 1/7: Initializing shared state...")
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
    logger.info("Step 2/7: Starting Telegram Bot...")
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
    logger.info("Step 3/7: Initializing clients...")
    await initialize_clients()

    # =================================================================
    # Step 4: Connect to Databases
    # =================================================================
    logger.info("Step 4/7: Connecting to databases...")
    await connect_all()

    # Keep Heroku server alive (if on Heroku)
    if ON_HEROKU:
        asyncio.create_task(ping_server())

    # =================================================================
    # Step 5: Load Banned Users and Verify Indexes
    # =================================================================
    logger.info("Step 5/7: Loading banned users...")
    b_users, b_chats = await db.get_banned()
    temp.BANNED_USERS = b_users
    temp.BANNED_CHATS = b_chats

    logger.info("Step 5/7: Verifying database indexes...")
    await ensure_all_indexes()
    logger.info("✅ Database Ready")

    # =================================================================
    # Step 6: Start Background Workers
    # =================================================================
    logger.info("Step 6/7: Starting background workers...")
    await start_background_workers()

    # =================================================================
    # Step 7: Setup Event Handlers
    # =================================================================
    logger.info("Step 7/7: Setting up event handlers...")
    setup_event_handlers()

    # =================================================================
    # Notify Success
    # =================================================================
    logger.info(f"{bot_info.first_name} with Pyrogram v{__version__} (Layer {layer}) started on @{bot_info.username}.")
    logger.info(LOG_STR)
    logger.info(script.LOGO)

    # Time logging
    tz = pytz.timezone('Asia/Kolkata')
    today = date.today()
    now = datetime.now(tz)
    time = now.strftime("%H:%M:%S %p")

    # Send startup message
    await Cine3600Bot.send_message(
        chat_id=LOG_CHANNEL,
        text=script.RESTART_TXT.format(today, time)
    )

    # =================================================================
    # Enter Idle Loop
    # =================================================================
    print('\n' + '=' * 50)
    print('✅ CINE3600 Bot is Online')
    print('📢 Waiting for messages...')
    print('=' * 50)

    logger.info("Bot started successfully. Entering idle loop...")

    # Publish startup event
    event_bus = get_event_bus()
    await event_bus.publish(
        Events.DB_CONNECTED,
        source="bot.py"
    )

    # Keep the bot running
    await idle()


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

    while True:
        try:
            await shared_state.update_bot_heartbeat()
            await asyncio.sleep(60)  # Every minute
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Heartbeat error: {e}")
            await asyncio.sleep(10)


if __name__ == '__main__':
    try:
        # Start heartbeat task
        loop.create_task(heartbeat_loop())

        # Run main bot
        loop.run_until_complete(Cine_start())
    except KeyboardInterrupt:
        logger.info('Service Stopped. Bye')
    except Exception as e:
        logger.exception(f"Fatal error: {e}")
