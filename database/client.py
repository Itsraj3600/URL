"""
Shared MongoDB client layer.

This is the single place in the whole project where MongoDB clients are
created. Every other database module imports the nodes / collections from
here instead of building its own ``MongoClient`` / ``AsyncIOMotorClient``.

It exposes up to three logical databases:

    Primary    -> DATABASE_URI
    Secondary  -> SECONDDB_URI   (optional)
    Tertiary   -> THIRDDB_URI    (optional)

All clients are asynchronous (Motor) and created with sane network timeouts
so a slow / unreachable database can never freeze the bot.
"""

import logging
import asyncio
from os import environ
from platform import node

from motor.motor_asyncio import AsyncIOMotorClient

from info import (
    DATABASE_URI,
    SECONDDB_URI,
    THIRDDB_URI,
    DATABASE_NAME,
    COLLECTION_NAME,
)

logger = logging.getLogger(__name__)

# --- Tunables -------------------------------------------------------------

# Network timeouts (ms). These guarantee the event loop never blocks forever
# waiting on a dead database.
SERVER_SELECTION_TIMEOUT_MS = int(environ.get("DB_SERVER_SELECTION_TIMEOUT_MS", 10000))
CONNECT_TIMEOUT_MS = int(environ.get("DB_CONNECT_TIMEOUT_MS", 10000))
SOCKET_TIMEOUT_MS = int(environ.get("DB_SOCKET_TIMEOUT_MS", 30000))

# Startup probe retries. A brief retry window avoids failing the worker on
# transient MongoDB startup / network delays.
CONNECT_RETRIES = int(environ.get("DB_CONNECT_RETRIES", 3))
CONNECT_RETRY_DELAY_SECONDS = float(environ.get("DB_CONNECT_RETRY_DELAY_SECONDS", 5))

# Connection pool tunables. Keep a warm pool without over-allocating sockets.
MAX_POOL_SIZE = int(environ.get("DB_MAX_POOL_SIZE", 100))
MIN_POOL_SIZE = int(environ.get("DB_MIN_POOL_SIZE", 5))
MAX_IDLE_TIME_MS = int(environ.get("DB_MAX_IDLE_TIME_MS", 60000))

# Per-database storage limit (MB). MongoDB Atlas free tier is 512 MB.
STORAGE_LIMIT_MB = float(environ.get("DB_STORAGE_LIMIT_MB", 512))

# Fill the current database until it crosses this fraction of the limit,
# then the router rolls over to the next database. (0.90 == 90%)
FILL_THRESHOLD = float(environ.get("DB_FILL_THRESHOLD", 0.90))


def _make_client(uri):
    """Create an AsyncIOMotorClient with timeouts, or ``None`` if no URI."""
    if not uri:
        return None
    return AsyncIOMotorClient(
        uri,
        serverSelectionTimeoutMS=SERVER_SELECTION_TIMEOUT_MS,
        connectTimeoutMS=CONNECT_TIMEOUT_MS,
        socketTimeoutMS=SOCKET_TIMEOUT_MS,
        maxPoolSize=MAX_POOL_SIZE,
        minPoolSize=MIN_POOL_SIZE,
        maxIdleTimeMS=MAX_IDLE_TIME_MS,
    )


class DBNode:
    """A single logical database (Primary / Secondary / Tertiary)."""

    def __init__(self, name, uri):
        self.name = name
        self.uri = uri
        self.client = _make_client(uri)
        self.healthy = False  # updated by connect()/ping()

        if self.client is not None:
            self.db = self.client[DATABASE_NAME]
            # Media collection used by ia_filterdb / router.
            self.media = self.db[COLLECTION_NAME]
            # Connection collection used by connections_mdb.
            self.connections = self.db["CONNECTION"]
        else:
            self.db = None
            self.media = None
            self.connections = None

    @property
    def configured(self):
        return self.client is not None

    async def ping(self):
        """Ping the server. Returns True on success, updates ``healthy``."""
        if self.client is None:
            self.healthy = False
            return False
        try:
            await self.client.admin.command("ping")
            self.healthy = True
            return True
        except Exception as e:
            self.healthy = False
            logger.error("Ping failed for %s DB: %s", self.name, e)
            return False

    def __repr__(self):
        return f"<DBNode {self.name} configured={self.configured} healthy={self.healthy}>"


# --- Build the nodes once at import time ---------------------------------
# (Motor clients are created lazily / non-blocking, so this is safe.)

PRIMARY = DBNode("Primary", DATABASE_URI)
SECONDARY = DBNode("Secondary", SECONDDB_URI)
TERTIARY = DBNode("Tertiary", THIRDDB_URI)

# Ordered list of every *configured* node (primary first). The router fills
# them in this order.
NODES = [n for n in (PRIMARY, SECONDARY, TERTIARY) if n.configured]


def configured_nodes():
    """All nodes that have a URI configured (order: primary -> tertiary)."""
    return list(NODES)


def healthy_nodes():
    """All configured nodes that passed their most recent health check."""
    return [n for n in NODES if n.healthy]


def media_collections():
    """Media collections for every healthy node (for reads / aggregation)."""
    return [n.media for n in NODES if n.healthy and n.media is not None]


async def connect_all():
    """
    Ping every configured database, log a clean startup report, and return
    the list of healthy nodes.

    Raises RuntimeError if not a single database is reachable.
    """
    if not NODES:
        raise RuntimeError(
            "No database configured. Set at least DATABASE_URI before starting."
        )

    last_error = None

    for attempt in range(CONNECT_RETRIES + 1):
        for node in NODES:
            logger.info("Connecting %s...", node.name)
            try:
                ok = await node.ping()

                if ok:
                    logger.info("%s connected successfully.", node.name)
                else:
                    logger.error("%s ping failed.", node.name)

            except Exception as exc:
                last_error = exc
                logger.exception("Unexpected error connecting to %s", node.name)

        alive = healthy_nodes()
        if alive:
            if len(alive) < len(NODES):
                logger.warning(
                    "Only %d/%d databases are online. Running in degraded mode.",
                    len(alive),
                    len(NODES),
                )

            return alive

        if attempt < CONNECT_RETRIES:
            delay = CONNECT_RETRY_DELAY_SECONDS * (2 ** attempt)
            logger.warning(
                "No databases reachable yet; retrying startup probe in %.1fs (%d/%d)...",
                delay,
                attempt + 1,
                CONNECT_RETRIES,
            )
            await asyncio.sleep(delay)

    if last_error is not None:
        logger.error("Could not connect to ANY database after retries: %s", last_error)
    else:
        logger.error("Could not connect to ANY database after retries.")

    return []
