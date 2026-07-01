"""
Global filters.

Asynchronous (Motor) and backed by the shared client. Global filter sets are
stored in their own collections inside the primary database.
"""

import logging

from pyrogram import enums

from info import COLLECTION_NAME
from database.client import get_primary

logger = logging.getLogger(__name__)


def _db():
    """The database that stores gfilter collections (primary)."""
    primary = get_primary()
    if primary is None or primary.db is None:
        raise RuntimeError("Primary MongoDB database is not initialized")
    return primary.db


async def add_gfilter(gfilters, text, reply_text, btn, file, alert):
    mycol = _db()[str(gfilters)]
    data = {
        "text": str(text),
        "reply": str(reply_text),
        "btn": str(btn),
        "file": str(file),
        "alert": str(alert),
    }
    try:
        await mycol.update_one({"text": str(text)}, {"$set": data}, upsert=True)
    except Exception as e:
        logger.exception("add_gfilter failed: %s", e)


async def find_gfilter(gfilters, name):
    mycol = _db()[str(gfilters)]
    try:
        results = await mycol.find({"text": name}).to_list(length=None)
        reply_text = btn = alert = fileid = None
        for file in results:
            reply_text = file["reply"]
            btn = file["btn"]
            fileid = file["file"]
            alert = file.get("alert")
        return reply_text, btn, alert, fileid
    except Exception as e:
        logger.error("find_gfilter failed: %s", e)
        return None, None, None, None


async def get_gfilters(gfilters):
    mycol = _db()[str(gfilters)]
    texts = []
    try:
        async for file in mycol.find():
            texts.append(file["text"])
    except Exception as e:
        logger.error("get_gfilters failed: %s", e)
    return texts


async def delete_gfilter(message, text, gfilters):
    mycol = _db()[str(gfilters)]
    myquery = {"text": text}
    query = await mycol.count_documents(myquery)
    if query == 1:
        await mycol.delete_one(myquery)
        await message.reply_text(
            f"'`{text}`'  deleted. I'll not respond to that gfilter anymore.",
            quote=True,
            parse_mode=enums.ParseMode.MARKDOWN,
        )
    else:
        await message.reply_text("Couldn't find that gfilter!", quote=True)


async def del_allg(message, gfilters):
    if str(gfilters) not in await _db().list_collection_names():
        await message.edit_text("Nothing to Remove !")
        return
    mycol = _db()[str(gfilters)]
    try:
        await mycol.drop()
        await message.edit_text("All gfilters has been removed !")
    except Exception as e:
        logger.error("del_allg failed: %s", e)
        await message.edit_text("Couldn't remove all gfilters !")


async def count_gfilters(gfilters):
    mycol = _db()[str(gfilters)]
    count = await mycol.count_documents({})
    return False if count == 0 else count


async def gfilter_stats():
    collections = await _db().list_collection_names()
    for reserved in ("CONNECTION", COLLECTION_NAME):
        if reserved in collections:
            collections.remove(reserved)

    totalcount = 0
    for collection in collections:
        mycol = _db()[collection]
        totalcount += await mycol.count_documents({})

    return len(collections), totalcount
