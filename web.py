"""
Web dyno entry point - runs ONLY the web server for streaming.
No Telegram bot handlers, no message processing.
Uses Telegram client with no_updates=True for file streaming only.
"""
import sys
import os
import logging
import logging.config
import asyncio

import pytz
from aiohttp import web
from pyrogram import Client

# Configure logging
logging.config.fileConfig('logging.conf')
logging.getLogger().setLevel(logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.getLogger("aiohttp").setLevel(logging.ERROR)
logging.getLogger("aiohttp.web").setLevel(logging.ERROR)

logger = logging.getLogger(__name__)


def validate_env_vars():
    """Validate critical environment variables before startup."""
    required_vars = {
        'BOT_TOKEN': 'Telegram Bot Token',
        'API_ID': 'Telegram API ID',
        'API_HASH': 'Telegram API Hash',
        'DATABASE_URI': 'MongoDB Connection URI',
        'DATABASE_NAME': 'MongoDB Database Name',
    }

    missing = []
    for var, description in required_vars.items():
        value = os.environ.get(var)
        if not value:
            missing.append(f"  - {var} ({description})")
        elif var == 'API_ID':
            try:
                int(value)
            except ValueError:
                missing.append(f"  - {var} must be a valid integer")

    if missing:
        logging.error("=" * 50)
        logging.error("WEB STARTUP FAILED: Missing or invalid environment variables:")
        for item in missing:
            logging.error(item)
        logging.error("=" * 50)
        sys.exit(1)


# Validate environment before proceeding
validate_env_vars()

from info import API_ID, API_HASH, BOT_TOKEN, PORT, MULTI_CLIENT, FQDN, HAS_SSL
from plugins import web_server
from cinebot import multi_clients, work_loads


async def start_streaming_client():
    """Start Telegram client for streaming with no_updates=True."""
    logger.info("Starting streaming client (no updates mode)...")

    # Client 0 is the main bot client for streaming
    streaming_client = Client(
        name="streamer",
        api_id=API_ID,
        api_hash=API_HASH,
        bot_token=BOT_TOKEN,
        no_updates=True,  # Critical: don't receive any updates
        in_memory=True
    )
    await streaming_client.start()

    multi_clients[0] = streaming_client
    work_loads[0] = 0

    logger.info("Streaming client started successfully")


async def web_main():
    """Initialize and run the web server."""
    logger.info("Initializing CINE3600 Web Server")

    # Start streaming client
    await start_streaming_client()

    # Setup web server
    app = web.AppRunner(await web_server())
    await app.setup()

    bind_address = "0.0.0.0"
    site = web.TCPSite(app, bind_address, PORT)

    await site.start()

    url = f"{'https' if HAS_SSL else 'http'}://{FQDN}/"
    logger.info(f"Web server started on {url}")

    # Keep running forever
    while True:
        await asyncio.sleep(3600)


if __name__ == "__main__":
    try:
        asyncio.run(web_main())
    except KeyboardInterrupt:
        logger.info("Web server stopped. Bye")
    except Exception:
        logging.exception("Fatal error while running web server.")
