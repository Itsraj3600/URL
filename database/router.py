"""
Database router.

Plugins never decide *which* database to read from or write to. They call
the helpers here and the router picks the right node:

    * Writes  -> fill-by-capacity load balancer (Primary until ~90% full,
                 then Secondary, then Tertiary) with automatic failover.
    * Reads   -> fan out across every healthy node and merge the results.

This means a new database can be added (or one can go offline) without
touching a single plugin.
"""

import datetime
import logging

from pymongo.errors import DuplicateKeyError

from database.client import NODES, healthy_nodes
from database.utils import has_capacity

logger = logging.getLogger(__name__)

# How many successful writes before we re-measure the current node's fill
# level. Re-running dbStats on every single insert would be far too slow
# while indexing hundreds of thousands of files.
WRITE_RECHECK_INTERVAL = 50

# Cached load-balancer state.
_write_node = None
_writes_since_check = 0


# --- Load balancer --------------------------------------------------------

async def select_write_node(force=False):
    """
    Choose the node that should receive new files using fill-by-capacity:
    the first healthy node that is still below the fill threshold. Offline
    nodes are skipped (failover).

    The choice is cached and only re-evaluated every
    ``WRITE_RECHECK_INTERVAL`` writes (or when ``force=True``).
    """
    global _write_node, _writes_since_check

    if not force and _write_node is not None and _write_node.healthy:
        if _writes_since_check < WRITE_RECHECK_INTERVAL:
            return _write_node

    # Re-evaluate. Walk nodes in priority order.
    for node in NODES:
        if not await node.ping():
            logger.warning("Skipping %s DB for writes (offline).", node.name)
            continue
        if await has_capacity(node):
            if node is not _write_node:
                logger.info("Load balancer: writing new files to %s DB.", node.name)
            _write_node = node
            _writes_since_check = 0
            return node
        logger.info("%s DB is above the fill threshold, trying next.", node.name)

    # Everything is full -> fall back to the last healthy node so we keep
    # accepting writes rather than losing data.
    for node in NODES:
        if node.healthy:
            logger.warning(
                "All databases are above the fill threshold. Still using %s DB.",
                node.name,
            )
            _write_node = node
            _writes_since_check = 0
            return node

    return None


# --- Writes ---------------------------------------------------------------

async def save_file(doc):
    """
    Insert a media document. ``doc`` must already contain ``_id``.

    Returns a ``(saved: bool, code: int)`` tuple:
        (True, 1)  -> saved
        (False, 0) -> duplicate / skipped
        (False, 2) -> error
    Follows Phase 6: insert first, treat ``DuplicateKeyError`` as "skip"
    instead of doing a separate existence check.
    """
    global _writes_since_check

    doc.setdefault("upload_date", datetime.datetime.utcnow())

    tried = set()
    while True:
        node = await select_write_node()
        if node is None:
            logger.error("No database available to save file.")
            return False, 2
        if node.name in tried:
            # We already failed on every reachable node.
            logger.error("All candidate databases failed for this write.")
            return False, 2
        tried.add(node.name)

        try:
            await node.media.insert_one(doc)
            _writes_since_check += 1
            return True, 1
        except DuplicateKeyError:
            return False, 0
        except Exception as e:
            logger.error("Write to %s DB failed (%s). Failing over.", node.name, e)
            node.healthy = False
            await select_write_node(force=True)
            # loop and retry on the next node


async def delete_file(query):
    """
    Delete matching documents from EVERY healthy node (a file could live on
    any database). Returns total deleted count.
    """
    deleted = 0
    for node in healthy_nodes():
        try:
            result = await node.media.delete_many(query)
            deleted += result.deleted_count
        except Exception as e:
            logger.error("Delete on %s DB failed: %s", node.name, e)
    return deleted


async def delete_one(query):
    """Delete a single document, scanning healthy nodes until one matches."""
    for node in healthy_nodes():
        try:
            result = await node.media.delete_one(query)
            if result.deleted_count:
                return result.deleted_count
        except Exception as e:
            logger.error("Delete on %s DB failed: %s", node.name, e)
    return 0


async def drop_all():
    """Drop the media collection on every healthy node."""
    for node in healthy_nodes():
        try:
            await node.media.drop()
        except Exception as e:
            logger.error("Drop on %s DB failed: %s", node.name, e)


# --- Reads ----------------------------------------------------------------

async def count_documents(query=None):
    """Total media documents matching ``query`` across all healthy nodes."""
    query = query or {}
    total = 0
    for node in healthy_nodes():
        try:
            total += await node.media.count_documents(query)
        except Exception as e:
            logger.error("count_documents on %s DB failed: %s", node.name, e)
    return total


async def search_files(filter_query, max_results, offset):
    """
    Paginate over every healthy node as one logical, ordered collection
    (Primary -> Secondary -> Tertiary, newest first within each).

    Returns ``(files, next_offset, total_results)`` where ``files`` is a list
    of raw documents (dicts).
    """
    nodes = healthy_nodes()

    # Per-node counts let us walk the global offset correctly.
    counts = []
    total = 0
    for node in nodes:
        try:
            c = await node.media.count_documents(filter_query)
        except Exception as e:
            logger.error("count on %s DB failed: %s", node.name, e)
            c = 0
        counts.append(c)
        total += c

    results = []
    remaining = max_results
    skip = offset
    for node, count in zip(nodes, counts):
        if remaining <= 0:
            break
        if skip >= count:
            skip -= count
            continue
        try:
            cursor = (
                node.media.find(filter_query)
                .sort("$natural", -1)
                .skip(skip)
                .limit(remaining)
            )
            batch = await cursor.to_list(length=remaining)
        except Exception as e:
            logger.error("search on %s DB failed: %s", node.name, e)
            batch = []
        results.extend(batch)
        remaining -= len(batch)
        skip = 0

    next_offset = offset + len(results)
    if next_offset >= total:
        next_offset = ""
    return results, next_offset, total


async def find_all(filter_query):
    """
    Return ALL documents matching ``filter_query`` across healthy nodes plus
    the total. Used by the "bad files" cleanup flow.
    """
    files = []
    for node in healthy_nodes():
        try:
            cursor = node.media.find(filter_query).sort("$natural", -1)
            files.extend(await cursor.to_list(length=None))
        except Exception as e:
            logger.error("find_all on %s DB failed: %s", node.name, e)
    return files, len(files)


async def find_one(filter_query):
    """Return the first matching document from any healthy node, or None."""
    for node in healthy_nodes():
        try:
            doc = await node.media.find_one(filter_query)
            if doc:
                return doc
        except Exception as e:
            logger.error("find_one on %s DB failed: %s", node.name, e)
    return None
