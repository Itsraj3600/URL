"""
Worker dyno entry point - runs ONLY the Telegram bot.
Handles all message processing, commands, filters, indexing, etc.
NO web server - that runs on the web dyno.
"""
import sys
import os
import glob
import importlib
import logging
import logging.config
import asyncio
<<<<<<< HEAD

from database.client import connect_all, get_primary
from database.utils import ensure_all_indexes
from database.schema import setup_production_schema
from database.users_chats_db import db
from info import *
from utils import temp
from Script import script
from handler_loader import load_handlers
from util.keepalive import ping_server
from cinebot import Cine3600Bot
from cinebot.clients import initialize_clients
from services.shared_state import initialize_shared_state, get_shared_state
from core import get_event_bus, Events
from core.startup import validate_startup
from core.shutdown import register_graceful_shutdown
from workers.heartbeat import WorkerHeartbeat
=======
from pathlib import Path
from datetime import date, datetime

import pytz
from pyrogram import Client, idle, __version__
from pyrogram.raw.all import layer
from pymongo.errors import OperationFailure


def validate_env_vars():
    """Validate critical environment variables before startup."""
    required_vars = {
        'BOT_TOKEN': 'Telegram Bot Token',
        'API_ID': 'Telegram API ID',
        'API_HASH': 'Telegram API Hash',
        'DATABASE_URI': 'MongoDB Connection URI',
        'DATABASE_NAME': 'MongoDB Database Name',
        'LOG_CHANNEL': 'Log Channel ID',
    }

    missing = []
    for var, description in required_vars.items():
        value = os.environ.get(var)
        if not value:
            missing.append(f"  - {var} ({description})")
        elif var in ('API_ID', 'LOG_CHANNEL'):
            try:
                int(value)
            except ValueError:
                missing.append(f"  - {var} must be a valid integer")

    if missing:
        logging.error("=" * 50)
        logging.error("WORKER STARTUP FAILED: Missing or invalid environment variables:")
        for item in missing:
            logging.error(item)
        logging.error("=" * 50)
        logging.error("Please set these variables and restart the bot.")
        sys.exit(1)
>>>>>>> e53efdf1209bcb685f12472c3a19152e71fddbda


# Configure logging
logging.config.fileConfig('logging.conf')
logging.getLogger().setLevel(logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.getLogger("imdbpy").setLevel(logging.ERROR)
logging.getLogger("aiohttp").setLevel(logging.ERROR)
logging.getLogger("aiohttp.web").setLevel(logging.ERROR)

# Validate environment before proceeding
validate_env_vars()

<<<<<<< HEAD
=======
from database.ia_filterdb import Media
from database.users_chats_db import db
from info import *
from utils import temp
from Script import script
from lazybot import create_bot_client
from util.keepalive import ping_server
from lazybot.clients import initialize_clients

ppath = "plugins/*.py"
files = glob.glob(ppath)

# Exclude web_server plugin from worker - it runs on web dyno
files = [f for f in files if 'web_server' not in f and 'route' not in f]

# Create and start the bot client
LazyPrincessBot = create_bot_client()
LazyPrincessBot.start()
if __name__ == "__main__":
    asyncio.run(Lazy_start())

>>>>>>> e53efdf1209bcb685f12472c3a19152e71fddbda

async def Lazy_start():
    logger = logging.getLogger(__name__)
    logger.info("Initializing The Movie Provider Bot (Worker)")

    bot_info = await LazyPrincessBot.get_me()
    LazyPrincessBot.username = bot_info.username

    await initialize_clients(LazyPrincessBot)

    for name in files:
        with open(name):
            patt = Path(name)
            plugin_name = patt.stem
            plugins_dir = Path(f"plugins/{plugin_name}.py")
            import_path = f"plugins.{plugin_name}"

            spec = importlib.util.spec_from_file_location(import_path, plugins_dir)
            load = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(load)
            sys.modules[import_path] = load

            logger.debug(f"Plugin loaded: {plugin_name}")

<<<<<<< HEAD
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
    load_handlers()
    await Cine3600Bot.start()
    # Get bot info
    bot_info = await Cine3600Bot.get_me()
    Cine3600Bot.username = bot_info.username
    temp.ME = bot_info.id
    temp.U_NAME = bot_info.username
    temp.B_NAME = bot_info.first_name

    # ================= DEBUG START =================
    
    print("is_connected =", Cine3600Bot.is_connected)
    print("no_updates =", getattr(Cine3600Bot, "no_updates", "NOT FOUND"))
    print("workers =", getattr(Cine3600Bot, "workers", "NOT FOUND"))

    print("\n" + "=" * 80)
    print("CINE3600 DEBUG")
    print("=" * 80)

    print("Bot class:", type(Cine3600Bot))
    print("Working Directory:", os.getcwd())
    print("Plugins Exists:", os.path.isdir("plugins"))

    if os.path.isdir("plugins"):
        print("\nPlugin Files:")
        for f in sorted(os.listdir("plugins")):
            print(" -", f)

    print("\nDispatcher Groups:")
    total = 0

    for group, handlers in Cine3600Bot.dispatcher.groups.items():
        print(f"\nGroup {group}: {len(handlers)} handlers")
        total += len(handlers)

        for handler in handlers:
            try:
                cb = handler.callback
                print(f"   {cb.__module__}.{cb.__name__}")
            except Exception as e:
                print(f"   {handler} ({e})")

    print(f"\nTOTAL HANDLERS: {total}")
    print("=" * 80)

    # ================= DEBUG END =================

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
    primary = get_primary()

    if primary is None or primary.client is None:
        raise RuntimeError("Primary MongoDB client was not initialized")

    if not database_ready:
        logger.warning(
            "No MongoDB nodes are currently reachable. Continuing in degraded mode."
        )

    if database_ready:
        try:
            await setup_production_schema(primary.client)
        except Exception as e:
            logger.exception(f"Schema setup failed: {e}")
            raise

    # Keep Heroku server alive (if on Heroku)
=======
>>>>>>> e53efdf1209bcb685f12472c3a19152e71fddbda
    if ON_HEROKU:
        asyncio.create_task(ping_server())

    b_users, b_chats = await db.get_banned()
    temp.BANNED_USERS = b_users
    temp.BANNED_CHATS = b_chats

    # -----------------------------
    # MongoDB Index Initialization
    # -----------------------------
    try:
        await Media.ensure_indexes()
        logging.info("Database indexes verified successfully.")
    except OperationFailure as e:
        if e.code == 85:
            logging.warning(
                "Index already exists with different options. "
                "Skipping automatic index creation."
            )
        else:
            raise
    except Exception as e:
        logging.exception(f"Failed to ensure indexes: {e}")

    temp.ME = bot_info.id
    temp.U_NAME = bot_info.username
    temp.B_NAME = bot_info.first_name

    LazyPrincessBot.username = "@" + bot_info.username

    logging.info(
        f"{bot_info.first_name} with Pyrogram v{__version__} "
        f"(Layer {layer}) started on {bot_info.username}."
    )

    logging.info(LOG_STR)
    logging.info(script.LOGO)

    tz = pytz.timezone("Asia/Kolkata")
    today = date.today()
    now = datetime.now(tz)
    current_time = now.strftime("%H:%M:%S %p")

    try:
        await LazyPrincessBot.send_message(
            chat_id=LOG_CHANNEL,
            text=script.RESTART_TXT.format(today, current_time)
        )
    except Exception as e:
        logging.warning(f"Unable to send restart message: {e}")

    logging.info("Bot Worker Started Successfully.")

    await idle()


if __name__ == "__main__":
    try:
        loop.run_until_complete(Lazy_start())
    except KeyboardInterrupt:
        logging.info("Service Stopped. Bye")
    except Exception:
        logging.exception("Fatal error while starting the bot.")
