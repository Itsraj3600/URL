import logging
import logging.config

logging.config.fileConfig('logging.conf')
logging.getLogger().setLevel(logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.getLogger("imdbpy").setLevel(logging.ERROR)
logging.getLogger("aiohttp").setLevel(logging.ERROR)
logging.getLogger("aiohttp.web").setLevel(logging.ERROR)

from typing import Union, Optional, AsyncGenerator
from pyrogram import Client, types

from database.ia_filterdb import Media
from info import *
from utils import temp


class LazyPrincessXBot(Client):

    def __init__(self):
        super().__init__(
            name=SESSION,
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            workers=50,
            plugins={"root": "plugins"},
            sleep_threshold=5,
        )

    async def iter_messages(
        self,
        chat_id: Union[int, str],
        limit: int,
        offset: int = 0,
    ) -> Optional[AsyncGenerator["types.Message", None]]:
        """Iterate through a chat sequentially."""
        current = offset
        while True:
            new_diff = min(200, limit - current)
            if new_diff <= 0:
                return
            messages = await self.get_messages(chat_id, list(range(current, current+new_diff+1)))
            for message in messages:
                yield message
                current += 1


# Shared state for multi-client streaming
multi_clients = {}
work_loads = {}

# Bot client - only created when imported by worker (bot.py)
LazyPrincessBot = None


def create_bot_client():
    """Create the main bot client with plugin handlers. Called by bot.py only."""
    global LazyPrincessBot
    if LazyPrincessBot is None:
        LazyPrincessBot = LazyPrincessXBot()
    return LazyPrincessBot

