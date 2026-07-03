import sys
import glob
import importlib
from pathlib import Path
from pyrogram import idle
import logging
import logging.config
from pymongo.errors import OperationFailure

# Get logging configurations
logging.config.fileConfig('logging.conf')
logging.getLogger().setLevel(logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.getLogger("imdbpy").setLevel(logging.ERROR)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logging.getLogger("aiohttp").setLevel(logging.ERROR)
logging.getLogger("aiohttp.web").setLevel(logging.ERROR)

from pyrogram import Client, __version__
from pyrogram.raw.all import layer
from database.ia_filterdb import Media
from database.users_chats_db import db
from info import *
from utils import temp
from typing import Union, Optional, AsyncGenerator
from pyrogram import types
from Script import script
from datetime import date, datetime
import pytz
from aiohttp import web
from plugins import web_server

import asyncio
from pyrogram import idle
from lazybot import LazyPrincessBot
from util.keepalive import ping_server
from lazybot.clients import initialize_clients

ppath = "plugins/*.py"
files = glob.glob(ppath)

LazyPrincessBot.start()
loop = asyncio.get_event_loop()


async def Lazy_start():
    print("\n")
    print("Initializing The Movie Provider Bot")

    bot_info = await LazyPrincessBot.get_me()
    LazyPrincessBot.username = bot_info.username

    await initialize_clients()

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

            print(f"The Movie Provider Imported => {plugin_name}")

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

    me = await LazyPrincessBot.get_me()

    temp.ME = me.id
    temp.U_NAME = me.username
    temp.B_NAME = me.first_name

    LazyPrincessBot.username = "@" + me.username

    logging.info(
        f"{me.first_name} with Pyrogram v{__version__} "
        f"(Layer {layer}) started on {me.username}."
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

    app = web.AppRunner(await web_server())
    await app.setup()

    bind_address = "0.0.0.0"
    await web.TCPSite(app, bind_address, PORT).start()

    logging.info("Bot Started Successfully.")

    await idle()


if __name__ == "__main__":
    try:
        loop.run_until_complete(Lazy_start())
    except KeyboardInterrupt:
        logging.info("Service Stopped. Bye 👋")
    except Exception:
        logging.exception("Fatal error while starting the bot.")
