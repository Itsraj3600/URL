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


# Configure logging
logging.config.fileConfig('logging.conf')
logging.getLogger().setLevel(logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.getLogger("imdbpy").setLevel(logging.ERROR)
logging.getLogger("aiohttp").setLevel(logging.ERROR)
logging.getLogger("aiohttp.web").setLevel(logging.ERROR)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Create asyncio event loop
loop = asyncio.get_event_loop()

async def Cine_start():
    print('\nInitializing CINE3600 Bot')

    await Cine3600Bot.start()
    bot_info = await Cine3600Bot.get_me()
    Cine3600Bot.username = bot_info.username
    await initialize_clients()

    # Connect to all configured databases (Primary / Secondary / Tertiary),
    # run health checks and verify indexes before serving anything.
    await connect_all()

    # Keep Heroku server alive (if on Heroku)
    if ON_HEROKU:
        asyncio.create_task(ping_server())

    # Banned users and chats setup
    b_users, b_chats = await db.get_banned()
    temp.BANNED_USERS = b_users
    temp.BANNED_CHATS = b_chats

    # Verify / create indexes on every healthy database. The router handles
    # which database new files are written to (fill-by-capacity + failover),
    # so no manual primary/secondary selection is needed here anymore.
    await ensure_all_indexes()
    logging.info("Database Ready")

    # Get bot details
    me = await Cine3600Bot.get_me()
    temp.ME = me.id
    temp.U_NAME = me.username
    temp.B_NAME = me.first_name
    Cine3600Bot.username = '@' + me.username
    logging.info(f"{me.first_name} with Pyrogram v{__version__} (Layer {layer}) started on {me.username}.")
    logging.info(LOG_STR)
    logging.info(script.LOGO)

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
    
    # Keep the bot running
    await idle()

if __name__ == '__main__':
    try:
        loop.run_until_complete(Cine_start())
    except KeyboardInterrupt:
        logging.info('Service Stopped. Bye 👋')
