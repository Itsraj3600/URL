# Search System Audit

## Overview
This document catalogs all functions involved in the search system of the CINE3600 bot.

---

## Database Layer Functions

### Function: `get_search_results()`
**File:** `database/ia_filterdb.py:247`

**Purpose:**
Searches MongoDB for movie/file titles matching a query. Core search function that returns paginated results.

**Called By:**
- `plugins/pm_filter.py:auto_filter()` - line 1204
- `plugins/pm_filter.py:next_page()` - line 164
- `plugins/pm_filter.py:advantage_spoll_choker()` - line 381
- `plugins/inline.py:answer()` - line 53

**Calls:**
- `_build_filter()` - builds MongoDB query
- `_load_search_cache()` - checks cache first
- `router.find_all()` - if cache miss, queries all DBs
- `_project_file()` - projects only needed fields
- `_store_search_cache()` - caches results
- `get_settings()` - gets group settings
- `save_group_settings()` - saves default settings if missing

**Database Queries:**
- `router.find_all(flt)` - queries all healthy database nodes
- Uses regex match on `file_name_normalized`, `file_name`, and optionally `caption`

**Returns:**
- `(files: List[FileResult], next_offset: str, total: int)` - paginated file results

---

### Function: `get_bad_files()`
**File:** `database/ia_filterdb.py:288`

**Purpose:**
Returns ALL matching files across all databases without pagination. Used for cleanup operations.

**Called By:**
- Admin cleanup functions

**Calls:**
- `_build_filter()` - builds MongoDB query
- `router.find_all()` - queries all healthy nodes

**Database Queries:**
- `router.find_all(flt)` - retrieves all matches

**Returns:**
- `(files: List[FileResult], total: int)` - all matching files

---

### Function: `get_file_details()`
**File:** `database/ia_filterdb.py:297`

**Purpose:**
Returns file document by encoded file_id.

**Called By:**
- `plugins/pm_filter.py:cb_handler()` - line 583, 633
- Start handler for deep links

**Calls:**
- `router.find_one()` - single document lookup

**Database Queries:**
- `router.find_one({"_id": query})` - exact ID match

**Returns:**
- `List[FileResult]` - single file wrapped in list or empty list

---

### Function: `_build_filter()`
**File:** `database/ia_filterdb.py:223`

**Purpose:**
Builds MongoDB filter query from user search string.

**Called By:**
- `get_search_results()`
- `get_bad_files()`

**Calls:**
- `normalize_title()` - normalizes search string

**Database Queries:**
- None (query builder only)

**Returns:**
- `dict` - MongoDB filter with `$or` regex conditions on file_name/caption

---

### Function: `normalize_title()`
**File:** `database/ia_filterdb.py:45`

**Purpose:**
Cleans and normalizes file names for better search matching. Removes release tags, brackets, special characters.

**Called By:**
- `_build_filter()`
- `_search_cache_key()`
- `save_file()` - when saving new files

**Database Queries:**
- None

**Returns:**
- `str` - normalized lowercase string

---

## Cache Functions

### Function: `_load_search_cache()`
**File:** `database/ia_filterdb.py:100`

**Purpose:**
Retrieves cached search results to avoid repeated DB queries.

**Called By:**
- `get_search_results()`

**Calls:**
- `_search_cache_prune()` - removes expired entries

**Database Queries:**
- None (in-memory OrderedDict cache)

**Returns:**
- `dict | None` - cached results or None

---

### Function: `_store_search_cache()`
**File:** `database/ia_filterdb.py:89`

**Purpose:**
Stores search results in in-memory cache with TTL.

**Called By:**
- `get_search_results()`

**Calls:**
- `_search_cache_prune()` - prunes before storing

**Database Queries:**
- None

**Returns:**
- None (stores in global `_SEARCH_CACHE`)

---

## Plugin Layer Functions

### Function: `auto_filter()`
**File:** `plugins/pm_filter.py:1193`

**Purpose:**
Main search handler for group messages. Triggers search on any text in groups.

**Called By:**
- `plugins/pm_filter.py:give_filter()` - line 45
- `plugins/pm_filter.py:advantage_spoll_choker()` - line 384

**Calls:**
- `get_settings()` - fetches group settings
- `get_search_results()` - performs search
- `get_poster()` - fetches IMDB metadata
- `get_shortlink()` - generates short URLs (conditional)
- `message.reply_photo()` / `message.reply_text()` - sends results

**Database Queries:**
- Indirect via `get_search_results()`
- Direct via `get_settings()`

**Returns:**
- None (sends Telegram message)

---

### Function: `next_page()`
**File:** `plugins/pm_filter.py:149`

**Purpose:**
Handles pagination callback for browsing more search results.

**Called By:**
- Callback handler via regex `^next`

**Calls:**
- `get_search_results()` - fetches next page
- `get_settings()` - gets group settings
- `get_shortlink()` - URL shortening for non-premium

**Database Queries:**
- Indirect via `get_search_results()`

**Returns:**
- None (edits message with new buttons)

---

### Function: `answer()`
**File:** `plugins/inline.py:23`

**Purpose:**
Handles inline search queries (@bot search_term).

**Called By:**
- Pyrogram decorator `@Client.on_inline_query()`

**Calls:**
- `active_connection()` - gets user's connected group
- `is_req_subscribed()` - checks channel subscription
- `get_search_results()` - performs search
- `get_size()` - formats file sizes

**Database Queries:**
- Indirect via `get_search_results()`
- Direct via `active_connection()`

**Returns:**
- None (answers inline query with results)

---

### Function: `advantage_spell_chok()`
**File:** `plugins/pm_filter.py:1475`

**Purpose:**
Google spell check fallback when no results found. Suggests correct movie names.

**Called By:**
- `auto_filter()` - when no results and spell_check enabled

**Calls:**
- `search_gagala()` - Google search for movie names
- `get_poster()` - IMDB lookup for suggestions
- `message.reply()` - sends suggestions

**Database Queries:**
- None directly

**Returns:**
- None (sends suggestion message)

---

### Function: `manual_filters()`
**File:** `plugins/pm_filter.py:1529`

**Purpose:**
Checks message against custom group filters before auto-search.

**Called By:**
- `give_filter()` - line 43

**Calls:**
- `get_filters()` - retrieves group's custom filters
- `find_filter()` - gets filter content

**Database Queries:**
- `filters_mdb.get_filters()`
- `filters_mdb.find_filter()`

**Returns:**
- `bool` - False if no filter matched (proceed to auto_filter)

---

## Router Functions (Multi-DB)

### Function: `find_all()`
**File:** `database/router.py:224`

**Purpose:**
Queries all healthy database nodes and merges results.

**Called By:**
- `get_search_results()`
- `get_bad_files()`

**Calls:**
- `healthy_nodes()` - gets available nodes
- `node.media.find()` - queries each node

**Database Queries:**
- `node.media.find(filter_query)` on each healthy node

**Returns:**
- `(files: List[dict], total: int)` - merged results from all nodes

---

### Function: `find_one()`
**File:** `database/router.py:239`

**Purpose:**
Finds single document across all healthy nodes.

**Called By:**
- `get_file_details()`

**Database Queries:**
- `node.media.find_one(filter_query)` on each node until found

**Returns:**
- `dict | None` - document or None

---

## Performance Notes

1. **Cache Hit Rate:** In-memory OrderedDict cache with 600s TTL and 1000 max entries
2. **Multi-DB Queries:** Fan-out to all healthy nodes for reads
3. **Regex Search:** Uses MongoDB regex on normalized file_name field
4. **Pagination:** Efficient offset-based pagination in `router.search_files()`

## Optimization Opportunities

1. Cache is in-memory per process - lost on restart
2. Regex queries may be slow on large collections
3. No text index configured for file_name_normalized
4. Pagination uses skip() which is O(n) for large offsets
