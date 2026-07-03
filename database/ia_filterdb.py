import logging
from struct import pack
import re
import base64
from pyrogram.file_id import FileId
from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError
from motor.motor_asyncio import AsyncIOMotorClient
from info import DATABASE_URI, DATABASE_NAME, COLLECTION_NAME, USE_CAPTION_FILTER, MAX_B_TN
from utils import get_settings, save_group_settings

logger = logging.getLogger(__name__)


class _LazyMediaCollection:
    def __init__(self, uri, database_name, collection_name):
        self._uri = uri
        self._database_name = database_name
        self._collection_name = collection_name
        self._client = None
        self._db = None
        self._collection = None

    def _ensure_collection(self):
        if self._collection is None:
            self._client = AsyncIOMotorClient(self._uri)
            self._db = self._client[self._database_name]
            self._collection = self._db[self._collection_name]
        return self._collection

    @property
    def collection(self):
        return self._ensure_collection()

    async def ensure_indexes(self):
        existing_indexes = await self.collection.index_information()
        for index_info in existing_indexes.values():
            if index_info.get("key") == [("file_name", ASCENDING)]:
                return

        await self.collection.create_index(
            [("file_name", ASCENDING)],
            name="idx_file_name",
        )

    async def count_documents(self, *args, **kwargs):
        return await self.collection.count_documents(*args, **kwargs)

    def find(self, *args, **kwargs):
        return self.collection.find(*args, **kwargs)


Media = _LazyMediaCollection(DATABASE_URI, DATABASE_NAME, COLLECTION_NAME)


def build_search_regex(query: str):
    """Build a regex pattern for file search.
    Returns compiled regex or None if pattern is invalid.
    """
    query = query.strip()
    if not query:
        raw_pattern = '.'
    elif ' ' not in query:
        raw_pattern = r'(\b|[\.\+\-_])' + query + r'(\b|[\.\+\-_])'
    else:
        raw_pattern = query.replace(' ', r'.*[\s\.\+\-_]')

    try:
        return re.compile(raw_pattern, flags=re.IGNORECASE)
    except re.error:
        return None


async def save_file(media):
    """Save file in database"""

    # TODO: Find better way to get same file_id for same media to avoid duplicates
    file_id, file_ref = unpack_new_file_id(media.file_id)
    file_name = re.sub(r"(_|\-|\.|\+)", " ", str(media.file_name))
    document = {
        "_id": file_id,
        "file_ref": file_ref,
        "file_name": file_name,
        "file_size": media.file_size,
        "file_type": media.file_type,
        "mime_type": media.mime_type,
        "caption": media.caption.html if media.caption else None,
    }

    try:
        await Media.collection.insert_one(document)
    except DuplicateKeyError:
        logger.warning(
            f'{getattr(media, "file_name", "NO_FILE")} is already saved in database'
        )
        return False, 0
    except Exception:
        logger.exception('Error occurred while saving file in database')
        return False, 2

    logger.info(f'{getattr(media, "file_name", "NO_FILE")} is saved to database')
    return True, 1



async def get_search_results(chat_id, query, file_type=None, max_results=10, offset=0, filter=False):
    """For given query return (results, next_offset)"""
    if chat_id is not None:
        settings = await get_settings(int(chat_id))
        try:
            if settings['max_btn']:
                max_results = 10
            else:
                max_results = int(MAX_B_TN)
        except KeyError:
            await save_group_settings(int(chat_id), 'max_btn', False)
            settings = await get_settings(int(chat_id))
            if settings['max_btn']:
                max_results = 10
            else:
                max_results = int(MAX_B_TN)

    regex = build_search_regex(query)
    if regex is None:
        return [], '', 0

    if USE_CAPTION_FILTER:
        filter = {'$or': [{'file_name': regex}, {'caption': regex}]}
    else:
        filter = {'file_name': regex}

    if file_type:
        filter['file_type'] = file_type

    total_results = await Media.count_documents(filter)
    next_offset = offset + max_results

    if next_offset > total_results:
        next_offset = ''

    cursor = Media.find(filter)
    cursor.sort('$natural', -1)
    cursor.skip(offset).limit(max_results)
    files = await cursor.to_list(length=max_results)

    return files, next_offset, total_results


async def get_bad_files(query, file_type=None, filter=False):
    """For given query return (results, next_offset)"""
    regex = build_search_regex(query)
    if regex is None:
        return [], 0

    if USE_CAPTION_FILTER:
        filter = {'$or': [{'file_name': regex}, {'caption': regex}]}
    else:
        filter = {'file_name': regex}

    if file_type:
        filter['file_type'] = file_type

    total_results = await Media.count_documents(filter)

    cursor = Media.find(filter)
    cursor.sort('$natural', -1)
    files = await cursor.to_list(length=total_results)

    return files, total_results

async def get_file_details(query):
    filter = {'file_id': query}
    cursor = Media.find(filter)
    filedetails = await cursor.to_list(length=1)
    return filedetails


def encode_file_id(s: bytes) -> str:
    r = b""
    n = 0

    for i in s + bytes([22]) + bytes([4]):
        if i == 0:
            n += 1
        else:
            if n:
                r += b"\x00" + bytes([n])
                n = 0

            r += bytes([i])

    return base64.urlsafe_b64encode(r).decode().rstrip("=")


def encode_file_ref(file_ref: bytes) -> str:
    return base64.urlsafe_b64encode(file_ref).decode().rstrip("=")


def unpack_new_file_id(new_file_id):
    """Return file_id, file_ref"""
    decoded = FileId.decode(new_file_id)
    file_id = encode_file_id(
        pack(
            "<iiqq",
            int(decoded.file_type),
            decoded.dc_id,
            decoded.media_id,
            decoded.access_hash
        )
    )
    file_ref = encode_file_ref(decoded.file_reference)
    return file_id, file_ref
