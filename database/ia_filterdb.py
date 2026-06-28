"""
Media file database access layer.

Fully asynchronous (Motor) and multi-database aware. All routing / load
balancing / failover lives in ``database.router``; this module just exposes
the same public names the rest of the project already imports:

    save_file, get_search_results, get_bad_files, get_file_details,
    unpack_new_file_id, Media

``Media`` is a thin proxy that fans operations out across every configured
database, so existing call sites like ``Media.collection.delete_one(...)``
and ``await Media.count_documents()`` keep working unchanged.
"""

import logging
import re
import base64
import time
from collections import OrderedDict
from struct import pack
from os import environ
from typing import Optional, Dict, List, Any, Union

from pyrogram.file_id import FileId

from info import USE_CAPTION_FILTER, MAX_B_TN
from utils import get_settings, save_group_settings
from database import router

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

SEARCH_CACHE_TTL_SECONDS = int(environ.get("SEARCH_CACHE_TTL_SECONDS", 600))
SEARCH_CACHE_MAX_ENTRIES = int(environ.get("SEARCH_CACHE_MAX_ENTRIES", 1000))
_SEARCH_CACHE = OrderedDict()

_RELEASE_TAG_RE = re.compile(
    r"\b(?:480p|720p|1080p|2160p|4k|x264|x265|hevc|hdrip|brrip|bluray|web[- ]?dl|web[- ]?rip|hdtv|dvdrip|camrip|aac|ddp\d(?:\.\d)?|10bit|multi|proper|remux|hdr)\b",
    re.IGNORECASE,
)
_BRACKET_TAG_RE = re.compile(r"[\[\(\{].*?[\]\)\}]")
_NON_WORD_RE = re.compile(r"[^\w\s]+")


def normalize_title(text: Optional[str]) -> str:
    """
    Normalize a movie/file title for search indexing.
    
    Removes brackets, tags, special characters, and normalizes whitespace.
    
    Args:
        text: The title to normalize
        
    Returns:
        Normalized title string in lowercase
    """
    text = (text or "").lower()
    text = _BRACKET_TAG_RE.sub(" ", text)
    text = text.replace("_", " ")
    text = _RELEASE_TAG_RE.sub(" ", text)
    text = _NON_WORD_RE.sub(" ", text)
    return re.sub(r"\s+", " ", text).strip()


def _search_cache_key(chat_id: int, requester_id: int, query: str, file_type: Optional[str] = None, filter_mode: bool = False) -> str:
    """
    Generate a cache key for search results.
    
    Args:
        chat_id: The chat ID for scoped searches
        requester_id: The user ID requesting the search
        query: The search query string
        file_type: Optional file type filter
        filter_mode: Whether filter mode is enabled
        
    Returns:
        Cache key string
    """
    return "|".join(
        [
            str(chat_id or 0),
            str(requester_id or 0),
            str(int(bool(filter_mode))),
            str(file_type or "*"),
            normalize_title(query),
        ]
    )


def _search_cache_prune() -> None:
    """
    Remove expired entries from the search cache and enforce max size limits.
    
    Removes entries older than SEARCH_CACHE_TTL_SECONDS and evicts oldest entries
    when cache exceeds SEARCH_CACHE_MAX_ENTRIES.
    """
    now = time.monotonic()
    expired = [key for key, value in _SEARCH_CACHE.items() if now - value["created_at"] > SEARCH_CACHE_TTL_SECONDS]
    for key in expired:
        _SEARCH_CACHE.pop(key, None)
    while len(_SEARCH_CACHE) > SEARCH_CACHE_MAX_ENTRIES:
        _SEARCH_CACHE.popitem(last=False)


def _project_file(doc):
    if not doc:
        return None
    return {
        "_id": doc.get("_id"),
        "file_name": doc.get("file_name"),
        "file_name_normalized": doc.get("file_name_normalized") or normalize_title(doc.get("file_name")),
        "file_size": doc.get("file_size"),
        "file_type": doc.get("file_type"),
        "caption": doc.get("caption"),
        "file_ref": doc.get("file_ref"),
    }


def _store_search_cache(chat_id, requester_id, query, file_type, filter_mode, files, total):
    _search_cache_prune()
    key = _search_cache_key(chat_id, requester_id, query, file_type=file_type, filter_mode=filter_mode)
    _SEARCH_CACHE[key] = {
        "created_at": time.monotonic(),
        "files": files,
        "total": total,
    }
    _SEARCH_CACHE.move_to_end(key)


def _load_search_cache(chat_id, requester_id, query, file_type=None, filter_mode=False):
    _search_cache_prune()
    key = _search_cache_key(chat_id, requester_id, query, file_type=file_type, filter_mode=filter_mode)
    cached = _SEARCH_CACHE.get(key)
    if cached is not None:
        _SEARCH_CACHE.move_to_end(key)
    return cached


# --- Result wrapper -------------------------------------------------------

class FileResult:
    """
    Attribute-style view over a raw Mongo document.

    Plugins access results as ``file.file_id`` / ``file.file_name`` etc.
    The encoded file id is stored as ``_id`` in Mongo, so ``file_id`` is
    transparently mapped to it.
    """

    __slots__ = ("_doc",)

    def __init__(self, doc):
        self._doc = doc

    def __getattr__(self, item):
        doc = object.__getattribute__(self, "_doc")
        if item == "file_id":
            return doc.get("_id")
        try:
            return doc[item]
        except KeyError:
            raise AttributeError(item)

    def __getitem__(self, item):
        if item == "file_id":
            return self._doc.get("_id")
        return self._doc[item]


def _wrap(docs):
    return [FileResult(d) for d in docs]


# --- Media proxy ----------------------------------------------------------

class _DeleteResult:
    def __init__(self, deleted_count):
        self.deleted_count = deleted_count


class _MultiCollection:
    """Broadcasts collection-level operations across all databases."""

    async def delete_one(self, query):
        return _DeleteResult(await router.delete_one(query))

    async def delete_many(self, query):
        return _DeleteResult(await router.delete_file(query))

    async def drop(self):
        await router.drop_all()


class _MediaProxy:
    """Backward-compatible stand-in for the old umongo ``Media`` document."""

    collection = _MultiCollection()

    async def count_documents(self, query=None):
        return await router.count_documents(query or {})

    def find(self, query):
        # Not used directly by plugins anymore, but kept for safety.
        raise NotImplementedError(
            "Use get_search_results / get_bad_files instead of Media.find()."
        )


Media = _MediaProxy()
# Legacy alias: a second physical DB is no longer a separate document class,
# it is just another routed node. Kept so old imports don't break.
Media2 = Media


# --- Save -----------------------------------------------------------------

async def save_file(media):
    """Save a media file. Returns (saved: bool, status_code: int)."""
    file_id, file_ref = unpack_new_file_id(media.file_id)
    file_name = re.sub(r"(_|\-|\.|\+)", " ", str(media.file_name))

    try:
        doc = {
            "_id": file_id,
            "file_ref": file_ref,
            "file_name": file_name,
            "file_name_normalized": normalize_title(file_name),
            "file_size": media.file_size,
            "file_type": media.file_type,
            "mime_type": media.mime_type,
            "caption": media.caption.html if media.caption else None,
        }
    except Exception as e:
        logger.exception("Error building document for %s: %s",
                         getattr(media, "file_name", "NO_FILE"), e)
        return False, 2

    if not doc["file_name"] or doc["file_size"] is None:
        logger.error("Missing required fields for %s",
                     getattr(media, "file_name", "NO_FILE"))
        return False, 2

    saved, code = await router.save_file(doc)
    if saved:
        logger.info("%s saved to database.", file_name)
    elif code == 0:
        logger.warning("%s is already saved in database.", file_name)
    return saved, code


# --- Query helpers --------------------------------------------------------

def _build_filter(query, file_type=None):
    """Build a Mongo filter (regex on file_name / caption) from a raw query."""
    query = normalize_title(query)
    if not query:
        raw_pattern = "."
    else:
        raw_pattern = re.escape(query)

    try:
        regex = re.compile(raw_pattern, flags=re.IGNORECASE)
    except Exception as e:
        logger.error("Bad search pattern %r: %s", raw_pattern, e)
        return None

    if USE_CAPTION_FILTER:
        flt = {"$or": [{"normalized_name": regex}, {"file_name": regex}, {"caption": regex}]}
    else:
        flt = {"$or": [{"normalized_name": regex}, {"file_name": regex}]}

    if file_type:
        flt["file_type"] = file_type
    return flt


async def get_search_results(chat_id, query, file_type=None, max_results=10, offset=0, filter=False, requester_id=None):
    """For a given query return (results, next_offset, total_results)."""
    if chat_id is not None:
        settings = await get_settings(int(chat_id))
        try:
            max_results = 10 if settings["max_btn"] else int(MAX_B_TN)
        except KeyError:
            await save_group_settings(int(chat_id), "max_btn", False)
            settings = await get_settings(int(chat_id))
            max_results = 10 if settings["max_btn"] else int(MAX_B_TN)

    flt = _build_filter(query, file_type)
    if flt is None:
        return [], "", 0

    if max_results % 2 != 0:
        logger.info(
            "max_results is odd (%s); using %s to keep it even.",
            max_results, max_results + 1,
        )
        max_results += 1

    cached = _load_search_cache(chat_id, requester_id, query, file_type=file_type, filter_mode=filter)
    if cached is None:
        files, total = await router.find_all(flt)
        projected = [_project_file(file) for file in files]
        _store_search_cache(chat_id, requester_id, query, file_type, filter, projected, total)
        cached = _load_search_cache(chat_id, requester_id, query, file_type=file_type, filter_mode=filter)

    if cached is None:
        return [], "", 0

    files = cached["files"]
    total = cached["total"]
    start = max(int(offset or 0), 0)
    end = start + max_results
    page = files[start:end]
    next_offset = end if end < total else ""
    return _wrap(page), next_offset, total


async def get_bad_files(query, file_type=None, filter=False):
    """For a given query return (results, total_results) across all DBs."""
    flt = _build_filter(query, file_type)
    if flt is None:
        return [], 0
    files, total = await router.find_all(flt)
    return _wrap(files), total


async def get_file_details(query):
    """Return a list with the matching file document (by encoded file id)."""
    doc = await router.find_one({"_id": query})
    return _wrap([doc]) if doc else []


# --- File id (de)serialisation -------------------------------------------

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
    """Return (file_id, file_ref)."""
    decoded = FileId.decode(new_file_id)
    file_id = encode_file_id(
        pack(
            "<iiqq",
            int(decoded.file_type),
            decoded.dc_id,
            decoded.media_id,
            decoded.access_hash,
        )
    )
    file_ref = encode_file_ref(decoded.file_reference)
    return file_id, file_ref
