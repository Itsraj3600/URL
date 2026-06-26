"""
Group connection store.

Multi-database aware and fully asynchronous (Motor). A user's connection
document can live on any node, so lookups scan every healthy database and
new documents are placed on whichever node the load balancer is currently
filling.
"""

import logging

from database.client import healthy_nodes
from database import router

logger = logging.getLogger(__name__)


async def _find_user_node(user_id):
    """Return the node whose CONNECTION collection holds this user, or None."""
    for node in healthy_nodes():
        try:
            if await node.connections.find_one({"_id": user_id}, {"_id": 1}):
                return node
        except Exception as e:
            logger.error("Lookup on %s DB failed: %s", node.name, e)
    return None


async def add_connection(group_id, user_id):
    group_details = {"group_id": group_id}

    node = await _find_user_node(user_id)
    if node is not None:
        try:
            query = await node.connections.find_one(
                {"_id": user_id}, {"_id": 0, "active_group": 0}
            )
            group_ids = [x["group_id"] for x in query["group_details"]]
            if group_id in group_ids:
                return False
            await node.connections.update_one(
                {"_id": user_id},
                {
                    "$push": {"group_details": group_details},
                    "$set": {"active_group": group_id},
                },
            )
            return True
        except Exception as e:
            logger.exception("add_connection update failed: %s", e)
            return False

    # New user -> place on the load-balanced write node (fallback: first DB).
    target = await router.select_write_node()
    if target is None or target.connections is None:
        alive = healthy_nodes()
        target = alive[0] if alive else None
    if target is None:
        logger.error("No database available to store connection.")
        return False

    data = {
        "_id": user_id,
        "group_details": [group_details],
        "active_group": group_id,
    }
    try:
        await target.connections.insert_one(data)
        return True
    except Exception as e:
        logger.exception("add_connection insert failed: %s", e)
        return False


async def active_connection(user_id):
    node = await _find_user_node(user_id)
    if node is None:
        return None
    try:
        query = await node.connections.find_one(
            {"_id": user_id}, {"_id": 0, "group_details": 0}
        )
        group_id = query["active_group"]
        return int(group_id) if group_id is not None else None
    except Exception as e:
        logger.error("active_connection failed: %s", e)
        return None


async def all_connections(user_id):
    node = await _find_user_node(user_id)
    if node is None:
        return None
    try:
        query = await node.connections.find_one(
            {"_id": user_id}, {"_id": 0, "active_group": 0}
        )
        return [x["group_id"] for x in query["group_details"]]
    except Exception as e:
        logger.error("all_connections failed: %s", e)
        return None


async def if_active(user_id, group_id):
    node = await _find_user_node(user_id)
    if node is None:
        return False
    try:
        query = await node.connections.find_one(
            {"_id": user_id}, {"_id": 0, "group_details": 0}
        )
        return query is not None and query["active_group"] == group_id
    except Exception as e:
        logger.error("if_active failed: %s", e)
        return False


async def make_active(user_id, group_id):
    node = await _find_user_node(user_id)
    if node is None:
        return False
    try:
        update = await node.connections.update_one(
            {"_id": user_id}, {"$set": {"active_group": group_id}}
        )
        return update.modified_count != 0
    except Exception as e:
        logger.error("make_active failed: %s", e)
        return False


async def make_inactive(user_id):
    node = await _find_user_node(user_id)
    if node is None:
        return False
    try:
        update = await node.connections.update_one(
            {"_id": user_id}, {"$set": {"active_group": None}}
        )
        return update.modified_count != 0
    except Exception as e:
        logger.error("make_inactive failed: %s", e)
        return False


async def delete_connection(user_id, group_id):
    node = await _find_user_node(user_id)
    if node is None:
        return False
    try:
        update = await node.connections.update_one(
            {"_id": user_id},
            {"$pull": {"group_details": {"group_id": group_id}}},
        )
        if update.modified_count == 0:
            return False

        query = await node.connections.find_one({"_id": user_id}, {"_id": 0})
        if query and len(query["group_details"]) >= 1:
            if query["active_group"] == group_id:
                prvs_group_id = query["group_details"][-1]["group_id"]
                await node.connections.update_one(
                    {"_id": user_id}, {"$set": {"active_group": prvs_group_id}}
                )
        else:
            await node.connections.update_one(
                {"_id": user_id}, {"$set": {"active_group": None}}
            )
        return True
    except Exception as e:
        logger.exception("delete_connection failed: %s", e)
        return False
