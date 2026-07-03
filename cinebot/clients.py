"""Client helpers for the Cinebot namespace."""

import logging

from . import LazyPrincessBot, multi_clients, work_loads

logger = logging.getLogger(__name__)


async def initialize_clients(client=None):
    active_client = client or LazyPrincessBot
    multi_clients.clear()
    work_loads.clear()
    multi_clients[0] = active_client
    work_loads[0] = 0
    logger.info("Initialized %d bot client(s).", len(multi_clients))
    return multi_clients