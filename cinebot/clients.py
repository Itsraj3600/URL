import asyncio
import logging

from info import *
from pyrogram import Client
from util.config_parser import TokenParser
from . import multi_clients, work_loads, Cine3600Bot


async def initialize_clients():
    multi_clients[0] = Cine3600Bot
    work_loads[0] = 0
    all_tokens = TokenParser().parse_from_env()
    if not all_tokens:
        print("No additional clients found, using default client")
        return

    async def start_client(client_id, token):
        try:
            print(f"Starting - Client {client_id}")
            # Use persistent sessions instead of in_memory=True to maintain session state
            client = await Client(
                name=str(client_id),
                api_id=API_ID,
                api_hash=API_HASH,
                bot_token=token,
                sleep_threshold=SLEEP_THRESHOLD,
                no_updates=True,
                in_memory=False  # Changed from True to False for persistent sessions
            ).start()
            work_loads[client_id] = 0
            return client_id, client
        except Exception:
            logging.error(f"Failed starting Client - {client_id} Error:", exc_info=True)

    # Start clients sequentially with staggered delays to avoid synchronous blocking
    clients_list = []
    for i, token in all_tokens.items():
        client_result = await start_client(i, token)
        if client_result:
            clients_list.append(client_result)
        # Small delay between client initializations to prevent Telegram rate limiting
        if i < len(all_tokens) - 1:
            await asyncio.sleep(1)
    
    multi_clients.update(dict(clients_list))
    if len(multi_clients) != 1:
        MULTI_CLIENT = True
        print("Multi-Client Mode Enabled")
    else:
        print("No additional clients were initialized, using default client")
