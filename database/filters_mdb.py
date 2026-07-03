import logging

from motor.motor_asyncio import AsyncIOMotorClient

from info import DATABASE_URI, DATABASE_NAME
from pyrogram import enums

logger = logging.getLogger(__name__)



class _LazyDatabase:
    def __init__(self, uri, database_name):
        self._uri = uri
        self._database_name = database_name
        self._client = None
        self._db = None

    def _ensure_db(self):
        if self._db is None:
            self._client = AsyncIOMotorClient(self._uri)
            self._db = self._client[self._database_name]
        return self._db

    def __getitem__(self, collection_name):
        return self._ensure_db()[collection_name]

    async def list_collection_names(self):
        return await self._ensure_db().list_collection_names()


db = _LazyDatabase(DATABASE_URI, DATABASE_NAME)


async def add_filter(grp_id, text, reply_text, btn, file, alert):
    col = db[str(grp_id)]

    data = {
        'text': str(text),
        'reply': str(reply_text),
        'btn': str(btn),
        'file': str(file),
        'alert': str(alert)
    }

    try:
        await col.update_one({'text': str(text)}, {"$set": data}, upsert=True)
    except Exception:
        logger.exception('Some error occured!', exc_info=True)


async def find_filter(group_id, name):
    col = db[str(group_id)]

    query = col.find({"text": name})
    try:
        async for file in query:
            reply_text = file['reply']
            btn = file['btn']
            fileid = file['file']
            try:
                alert = file['alert']
            except KeyError:
                alert = None
            return reply_text, btn, alert, fileid
    except Exception:
        pass
    return None, None, None, None


async def get_filters(group_id):
    col = db[str(group_id)]

    texts = []
    query = col.find()
    try:
        async for file in query:
            text = file['text']
            texts.append(text)
    except Exception:
        pass
    return texts


async def delete_filter(message, text, group_id):
    col = db[str(group_id)]

    myquery = {'text': text}
    query = await col.count_documents(myquery)
    if query == 1:
        await col.delete_one(myquery)
        await message.reply_text(
            f"'`{text}`'  deleted. I'll not respond to that filter anymore.",
            quote=True,
            parse_mode=enums.ParseMode.MARKDOWN
        )
    else:
        await message.reply_text("Couldn't find that filter!", quote=True)


async def del_all(message, group_id, title):
    collections = await db.list_collection_names()
    if str(group_id) not in collections:
        await message.edit_text(f"Nothing to remove in {title}!")
        return

    col = db[str(group_id)]
    try:
        await col.drop()
        await message.edit_text(f"All filters from {title} has been removed")
    except Exception:
        await message.edit_text("Couldn't remove all filters from group!")


async def count_filters(group_id):
    col = db[str(group_id)]

    count = await col.count_documents({})
    return False if count == 0 else count


async def filter_stats():
    collections = await db.list_collection_names()

    if "CONNECTION" in collections:
        collections.remove("CONNECTION")

    totalcount = 0
    for collection in collections:
        col = db[collection]
        count = await col.count_documents({})
        totalcount += count

    totalcollections = len(collections)

    return totalcollections, totalcount
