"""
Reusable database helpers shared across modules.

Home for cross-cutting database concerns: pinging, statistics, record
counting, index management and simple backup / restore. Keeping these here
avoids copy-pasting the same snippets into every module.
"""

import logging

from pymongo import ASCENDING, DESCENDING, TEXT
from pymongo.errors import OperationFailure

from database.client import (
    NODES,
    STORAGE_LIMIT_MB,
    FILL_THRESHOLD,
    healthy_nodes,
)

logger = logging.getLogger(__name__)

# Indexes maintained on every media collection. Designed for a catalogue of
# 600k+ files. ``_id`` (the encoded file_id) is indexed automatically.
MEDIA_INDEXES = [
    ([("file_name", ASCENDING)], {"name": "idx_file_name"}),
    ([("normalized_name", ASCENDING)], {"name": "idx_normalized_name"}),
    ([("normalized_name", ASCENDING), ("file_type", ASCENDING)], {"name": "idx_normalized_name_type"}),
    ([("file_type", ASCENDING)], {"name": "idx_file_type"}),
    ([("file_size", ASCENDING)], {"name": "idx_file_size"}),
    ([("upload_date", DESCENDING)], {"name": "idx_upload_date"}),
    (
        [("file_name", TEXT), ("caption", TEXT)],
        {"name": "txt_file_name_caption", "default_language": "english"},
    ),
]


# --- Health ---------------------------------------------------------------

async def ping(node):
    """Ping a single node. Returns True/False."""
    return await node.ping()


async def ping_all():
    """Ping every configured node. Returns {name: bool}."""
    result = {}
    for node in NODES:
        result[node.name] = await node.ping()
    return result


# --- Statistics -----------------------------------------------------------

async def db_stats(node):
    """
    Return raw ``dbStats`` plus derived size figures (in MB) for one node.
    Returns ``None`` if the node is offline.
    """
    if node.db is None:
        return None
    try:
        stats = await node.db.command("dbStats")
    except Exception as e:
        logger.error("dbStats failed for %s DB: %s", node.name, e)
        return None

    data_mb = stats.get("dataSize", 0) / (1024 * 1024)
    index_mb = stats.get("indexSize", 0) / (1024 * 1024)
    used_mb = round(data_mb + index_mb, 2)
    free_mb = round(STORAGE_LIMIT_MB - used_mb, 2)
    return {
        "name": node.name,
        "used_mb": used_mb,
        "free_mb": free_mb,
        "limit_mb": STORAGE_LIMIT_MB,
        "fraction_used": round(used_mb / STORAGE_LIMIT_MB, 4) if STORAGE_LIMIT_MB else 0,
        "raw": stats,
    }


async def has_capacity(node):
    """
    True if the node is below the fill threshold and can accept new writes.
    A node whose stats cannot be read is treated as having no capacity.
    """
    stats = await db_stats(node)
    if stats is None:
        return False
    return stats["fraction_used"] < FILL_THRESHOLD


async def database_statistics():
    """Aggregate stats across every node. Useful for an admin /dbstats cmd."""
    nodes_stats = []
    total_used = 0.0
    total_limit = 0.0
    for node in NODES:
        stats = await db_stats(node)
        if stats:
            nodes_stats.append(stats)
            total_used += stats["used_mb"]
            total_limit += stats["limit_mb"]
    return {
        "nodes": nodes_stats,
        "total_used_mb": round(total_used, 2),
        "total_limit_mb": round(total_limit, 2),
        "total_free_mb": round(total_limit - total_used, 2),
    }


async def count_records(collection, query=None):
    """Count documents in a collection (safe wrapper)."""
    try:
        return await collection.count_documents(query or {})
    except Exception as e:
        logger.error("count_records failed: %s", e)
        return 0


async def total_media_count(query=None):
    """Total media documents across every healthy node."""
    total = 0
    for node in healthy_nodes():
        total += await count_records(node.media, query)
    return total


# --- Indexes --------------------------------------------------------------

async def ensure_indexes_for(collection, node_name="DB"):
    """Create the media indexes on a single collection (idempotent)."""
    for keys, options in MEDIA_INDEXES:
        try:
            await collection.create_index(keys, **options)
        except OperationFailure as e:
            # Most common cause: an index with the same name but different
            # options already exists. Log and continue instead of crashing.
            logger.warning("Index %s on %s already exists / conflict: %s",
                           options.get("name"), node_name, e)
        except Exception as e:
            logger.error("Failed creating index %s on %s: %s",
                         options.get("name"), node_name, e)


async def ensure_all_indexes():
    """Verify / create indexes on every healthy node's media collection."""
    for node in healthy_nodes():
        await ensure_indexes_for(node.media, node.name)
    logger.info("Indexes verified.")


# --- Backup / Restore -----------------------------------------------------

async def backup_collection(collection, limit=0):
    """
    Read a collection into a list of dicts. ``limit=0`` means everything.
    Intended for small collections (settings, connections, filters) - not
    for the multi-hundred-thousand document media collection.
    """
    cursor = collection.find({})
    if limit:
        cursor = cursor.limit(limit)
    return await cursor.to_list(length=limit or None)


async def restore_collection(collection, documents, ordered=False):
    """
    Insert documents into a collection. Duplicate ``_id`` errors are ignored
    so a restore can be re-run safely.
    """
    if not documents:
        return 0
    try:
        result = await collection.insert_many(documents, ordered=ordered)
        return len(result.inserted_ids)
    except Exception as e:
        logger.warning("restore_collection completed with errors: %s", e)
        return 0
