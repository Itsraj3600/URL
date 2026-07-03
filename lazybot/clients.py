import asyncio
import logging
from info import *
from pyrogram import Client
from util.config_parser import TokenParser
from . import multi_clients, work_loads

logger = logging.getLogger(__name__)


async def initialize_clients(bot_client=None):
    """Initialize multi-client support for load balancing.
    If bot_client is provided (from worker), use it as client 0.
    """
    if bot_client is not None:
        multi_clients[0] = bot_client
        work_loads[0] = 0

    all_tokens = TokenParser().parse_from_env()
    if not all_tokens:
        logger.debug("No additional clients found, using default client")
        return

    async def start_client(client_id, token):
        try:
            logger.info(f"Starting client {client_id}")
            if client_id == len(all_tokens):
                await asyncio.sleep(2)
                logger.info("This will take some time, please wait...")
            client = await Client(
                name=str(client_id),
                api_id=API_ID,
                api_hash=API_HASH,
                bot_token=token,
                sleep_threshold=SLEEP_THRESHOLD,
                no_updates=True,
                in_memory=True
            ).start()
            work_loads[client_id] = 0
            return client_id, client
        except Exception:
            logger.error(f"Failed starting Client - {client_id}", exc_info=True)

    clients = await asyncio.gather(*[start_client(i, token) for i, token in all_tokens.items()])
    multi_clients.update(dict(clients))
    if len(multi_clients) != 1:
        logger.info("Multi-Client Mode Enabled")
    else:
        logger.debug("No additional clients were initialized, using default client")
