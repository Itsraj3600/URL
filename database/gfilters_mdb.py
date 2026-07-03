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


async def add_gfilter(gfilters, text, reply_text, btn, file, alert):
    col = db[str(gfilters)]

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


async def find_gfilter(gfilters, name):
    col = db[str(gfilters)]

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


async def get_gfilters(gfilters):
    col = db[str(gfilters)]

    texts = []
    query = col.find()
    try:
        async for file in query:
            text = file['text']
            texts.append(text)
    except Exception:
        pass
    return texts


async def delete_gfilter(message, text, gfilters):
    col = db[str(gfilters)]

    myquery = {'text': text}
    query = await col.count_documents(myquery)
    if query == 1:
        await col.delete_one(myquery)
        await message.reply_text(
            f"'`{text}`'  deleted. I'll not respond to that gfilter anymore.",
            quote=True,
            parse_mode=enums.ParseMode.MARKDOWN
        )
    else:
        await message.reply_text("Couldn't find that gfilter!", quote=True)


async def del_allg(message, gfilters):
    collections = await db.list_collection_names()
    if str(gfilters) not in collections:
        await message.edit_text("Nothing to Remove !")
        return

    col = db[str(gfilters)]
    try:
        await col.drop()
        await message.edit_text(f"All gfilters has been removed !")
    except Exception:
        await message.edit_text("Couldn't remove all gfilters !")


async def count_gfilters(gfilters):
    col = db[str(gfilters)]

    count = await col.count_documents({})
    return False if count == 0 else count


async def gfilter_stats():
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
