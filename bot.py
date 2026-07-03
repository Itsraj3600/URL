"""Worker dyno entry point for the Telegram bot."""

import asyncio
import logging
import logging.config
from datetime import date, datetime

import pytz
from pyrogram import __version__, idle
from pyrogram.raw.all import layer

from Script import script
from database.ia_filterdb import Media
from database.users_chats_db import db
from info import LOG_CHANNEL, LOG_STR, ON_HEROKU
from cinebot import Cine3600Bot
from cinebot.clients import initialize_clients
from util.keepalive import ping_server
from utils import temp


def configure_logging() -> None:
    logging.config.fileConfig("logging.conf")
    logging.getLogger().setLevel(logging.INFO)
    logging.getLogger("pyrogram").setLevel(logging.ERROR)
    logging.getLogger("imdbpy").setLevel(logging.ERROR)
    logging.getLogger("aiohttp").setLevel(logging.ERROR)
    logging.getLogger("aiohttp.web").setLevel(logging.ERROR)


async def start_bot() -> None:
    logger = logging.getLogger(__name__)
    logger.info("Starting bot worker")

    await initialize_clients(Cine3600Bot)

    await Cine3600Bot.start()
    bot_info = await Cine3600Bot.get_me()

    Cine3600Bot.username = bot_info.username
    temp.ME = bot_info.id
    temp.U_NAME = bot_info.username
    temp.B_NAME = bot_info.first_name

    total_handlers = 0
    for group, handlers in Cine3600Bot.dispatcher.groups.items():
        group_count = len(handlers)
        total_handlers += group_count
        logger.info("Handler group %s has %s handlers.", group, group_count)
    logger.info("Total registered handlers: %s", total_handlers)

    b_users, b_chats = await db.get_banned()
    temp.BANNED_USERS = b_users
    temp.BANNED_CHATS = b_chats

    try:
        await Media.ensure_indexes()
        logger.info("Database indexes verified successfully.")
    except Exception as exc:
        logger.warning("Failed to ensure indexes: %s", exc)

    if ON_HEROKU:
        asyncio.create_task(ping_server())

    tz = pytz.timezone("Asia/Kolkata")
    today = date.today()
    current_time = datetime.now(tz).strftime("%H:%M:%S %p")

    try:
        await Cine3600Bot.send_message(
            chat_id=LOG_CHANNEL,
            text=script.RESTART_TXT.format(today, current_time),
        )
    except Exception as exc:
        logger.warning("Unable to send restart message: %s", exc)

    logger.info(
        "%s with Pyrogram v%s (Layer %s) started on @%s.",
        bot_info.first_name,
        __version__,
        layer,
        bot_info.username,
    )
    logger.info(LOG_STR)
    logger.info(script.LOGO)
    logger.info("Bot worker started successfully.")

    await idle()


def main() -> None:
    configure_logging()
    asyncio.run(start_bot())


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.info("Service stopped.")
    except Exception:
        logging.exception("Fatal error while starting the bot.")
