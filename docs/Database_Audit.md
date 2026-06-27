# Database Audit

## Overview
This document catalogs all database functions and collections in the CINE3600 bot.

---

## Database Architecture

### Multi-Database Support
The system supports up to 3 MongoDB databases:
- **Primary** - `DATABASE_URI` (required)
- **Secondary** - `SECONDDB_URI` (optional)
- **Tertiary** - `THIRDDB_URI` (optional)

### Load Balancing Strategy
- **Writes:** Fill-by-capacity (fills Primary to 90%, then Secondary, then Tertiary)
- **Reads:** Fan-out to all healthy nodes, merge results

---

## Collections

### 1. Media Collection (`COLLECTION_NAME`)
**Database:** All nodes
**Purpose:** Stores indexed movie/file metadata

| Field | Type | Description |
|-------|------|-------------|
| `_id` | string | Encoded Telegram file_id |
| `file_ref` | string | Encoded file reference |
| `file_name` | string | Original file name |
| `file_name_normalized` | string | Normalized search name |
| `file_size` | int | File size in bytes |
| `file_type` | string | video/audio/document |
| `mime_type` | string | MIME type |
| `caption` | string | File caption |
| `upload_date` | datetime | When indexed |

**Indexes:** None explicitly defined (uses default `_id` index)

---

### 2. Users Collection (`users`)
**Database:** Primary
**Purpose:** Bot user records

| Field | Type | Description |
|-------|------|-------------|
| `id` | int | Telegram user ID |
| `name` | string | User display name |
| `ban_status` | dict | Ban info with `is_banned`, `ban_reason` |

---

### 3. Groups Collection (`groups`)
**Database:** Primary
**Purpose:** Group chat settings and status

| Field | Type | Description |
|-------|------|-------------|
| `id` | int | Telegram chat ID |
| `title` | string | Group title |
| `chat_status` | dict | Disabled status with `is_disabled`, `reason` |
| `settings` | dict | Group-specific settings |

---

### 4. Connections Collection (`CONNECTION`)
**Database:** All nodes
**Purpose:** User-group connections

| Field | Type | Description |
|-------|------|-------------|
| `_id` | string | Telegram user ID |
| `group_details` | array | List of connected groups |
| `active_group` | string | Currently active group ID |

---

### 5. Filter Collections (dynamic)
**Database:** Primary
**Purpose:** Per-group custom filters
**Naming:** Collection name = group_id as string

| Field | Type | Description |
|-------|------|-------------|
| `text` | string | Trigger keyword |
| `reply` | string | Reply text |
| `btn` | string | Button JSON |
| `file` | string | File ID |
| `alert` | string | Alert text |

---

### 6. Premium Users Collection (`uersz`)
**Database:** Primary
**Purpose:** Premium user data

| Field | Type | Description |
|-------|------|-------------|
| `id` | int | Telegram user ID |
| `expiry_time` | datetime | Premium expiry |
| `has_free_trial` | bool | Used free trial |

---

### 7. Requests Collection (`requests`)
**Database:** Primary
**Purpose:** Join request tracking

| Field | Type | Description |
|-------|------|-------------|
| `id` | int | Telegram user ID |

---

## Database Functions

### Media File Operations

#### `save_file(media)` - `database/ia_filterdb.py:187`
**Purpose:** Save a new media file to database
**Type:** WRITE
**Database:** Load-balanced to any healthy node
```python
# Returns: (saved: bool, status_code: int)
# status_code: 1 = saved, 0 = duplicate, 2 = error
```

---

#### `get_search_results(chat_id, query, ...)` - `database/ia_filterdb.py:247`
**Purpose:** Search for files with pagination
**Type:** READ
**Database:** All healthy nodes
```python
# Returns: (files, next_offset, total)
```

---

#### `get_bad_files(query, ...)` - `database/ia_filterdb.py:288`
**Purpose:** Get all matching files (no pagination)
**Type:** READ
**Database:** All healthy nodes
```python
# Returns: (files, total)
```

---

#### `get_file_details(query)` - `database/ia_filterdb.py:297`
**Purpose:** Get file by encoded file_id
**Type:** READ
**Database:** All healthy nodes (first match)
```python
# Returns: List[FileResult]
```

---

#### `delete_file(query)` - `database/router.py:122`
**Purpose:** Delete files from ALL nodes
**Type:** DELETE
**Database:** All healthy nodes
```python
# Returns: total_deleted: int
```

---

#### `delete_one(query)` - `database/router.py:137`
**Purpose:** Delete single file
**Type:** DELETE
**Database:** All healthy nodes until found
```python
# Returns: deleted_count: int
```

---

#### `count_documents(query)` - `database/router.py:160`
**Purpose:** Count total documents
**Type:** READ
**Database:** All healthy nodes
```python
# Returns: total: int
```

---

### Router Functions

#### `select_write_node(force)` - `database/router.py:37`
**Purpose:** Choose database for new writes (fill-by-capacity)
**Type:** Internal
**Logic:**
1. Check cached node (still healthy + under interval)
2. Walk nodes in priority order
3. Pick first healthy node under fill threshold (90%)
4. Fallback to last healthy if all full

---

#### `find_all(filter_query)` - `database/router.py:224`
**Purpose:** Query all nodes and merge results
**Type:** READ
**Database:** All healthy nodes
```python
# Returns: (files: List[dict], total: int)
```

---

#### `find_one(filter_query)` - `database/router.py:239`
**Purpose:** Find single document across nodes
**Type:** READ
**Database:** All healthy nodes
```python
# Returns: dict | None
```

---

### User Operations

#### `add_user(id, name)` - `database/users_chats_db.py:48`
**Purpose:** Add new bot user
**Type:** WRITE
**Collection:** `users`

---

#### `is_user_exist(id)` - `database/users_chats_db.py:52`
**Purpose:** Check if user exists
**Type:** READ
**Collection:** `users`

---

#### `total_users_count()` - `database/users_chats_db.py:56`
**Purpose:** Count total users
**Type:** READ
**Collection:** `users`

---

#### `ban_user(user_id, reason)` - `database/users_chats_db.py:67`
**Purpose:** Ban a user
**Type:** WRITE
**Collection:** `users`

---

#### `get_ban_status(id)` - `database/users_chats_db.py:74`
**Purpose:** Get user ban status
**Type:** READ
**Collection:** `users`

---

#### `delete_user(user_id)` - `database/users_chats_db.py:88`
**Purpose:** Delete user record
**Type:** DELETE
**Collection:** `users`

---

### Group Operations

#### `add_chat(chat, title)` - `database/users_chats_db.py:101`
**Purpose:** Add new group
**Type:** WRITE
**Collection:** `groups`

---

#### `get_chat(chat)` - `database/users_chats_db.py:106`
**Purpose:** Get group status
**Type:** READ
**Collection:** `groups`

---

#### `get_settings(id)` - `database/users_chats_db.py:122`
**Purpose:** Get group settings
**Type:** READ
**Collection:** `groups`
**Default Settings:**
```python
{
    'button': SINGLE_BUTTON,
    'botpm': P_TTI_SHOW_OFF,
    'file_secure': PROTECT_CONTENT,
    'imdb': IMDB,
    'spell_check': SPELL_CHECK_REPLY,
    'welcome': MELCOW_NEW_USERS,
    'auto_delete': AUTO_DELETE,
    'auto_ffilter': AUTO_FFILTER,
    'max_btn': MAX_BTN,
    'template': IMDB_TEMPLATE,
    'shortlink': SHORTLINK_URL,
    'shortlink_api': SHORTLINK_API,
    'is_shortlink': IS_SHORTLINK,
    'tutorial': TUTORIAL,
    'is_tutorial': IS_TUTORIAL
}
```

---

#### `update_settings(id, settings)` - `database/users_chats_db.py:118`
**Purpose:** Update group settings
**Type:** WRITE
**Collection:** `groups`

---

#### `disable_chat(chat, reason)` - `database/users_chats_db.py:146`
**Purpose:** Disable a group
**Type:** WRITE
**Collection:** `groups`

---

#### `total_chat_count()` - `database/users_chats_db.py:154`
**Purpose:** Count total groups
**Type:** READ
**Collection:** `groups`

---

### Connection Operations

#### `add_connection(group_id, user_id)` - `database/connections_mdb.py:29`
**Purpose:** Add user-group connection
**Type:** WRITE
**Database:** Load-balanced

---

#### `active_connection(user_id)` - `database/connections_mdb.py:75`
**Purpose:** Get user's active group
**Type:** READ
**Database:** All healthy nodes

---

#### `all_connections(user_id)` - `database/connections_mdb.py:90`
**Purpose:** Get all user's connections
**Type:** READ
**Database:** All healthy nodes

---

#### `delete_connection(user_id, group_id)` - `database/connections_mdb.py:146`
**Purpose:** Remove a connection
**Type:** WRITE
**Database:** User's node

---

### Filter Operations

#### `add_filter(grp_id, text, reply_text, btn, file, alert)` - `database/filters_mdb.py:24`
**Purpose:** Add custom filter
**Type:** WRITE
**Collection:** `{grp_id}`

---

#### `find_filter(group_id, name)` - `database/filters_mdb.py:39`
**Purpose:** Get filter content
**Type:** READ
**Collection:** `{grp_id}`

---

#### `get_filters(group_id)` - `database/filters_mdb.py:55`
**Purpose:** List all filter keywords
**Type:** READ
**Collection:** `{grp_id}`

---

#### `delete_filter(message, text, group_id)` - `database/filters_mdb.py:66`
**Purpose:** Delete a filter
**Type:** DELETE
**Collection:** `{grp_id}`

---

#### `count_filters(group_id)` - `database/filters_mdb.py:94`
**Purpose:** Count filters in group
**Type:** READ
**Collection:** `{grp_id}`

---

### Premium Operations

#### `get_user(user_id)` - `database/users_chats_db.py:166`
**Purpose:** Get premium user data
**Type:** READ
**Collection:** `uersz`

---

#### `update_user(user_data)` - `database/users_chats_db.py:169`
**Purpose:** Update premium user
**Type:** WRITE
**Collection:** `uersz`

---

#### `has_premium_access(user_id)` - `database/users_chats_db.py:172`
**Purpose:** Check premium status
**Type:** READ
**Collection:** `uersz`

---

#### `give_free_trial(user_id)` - `database/users_chats_db.py:215`
**Purpose:** Grant free trial
**Type:** WRITE
**Collection:** `uersz`

---

## Index Recommendations

### Media Collection
```javascript
// Text search index
db.media.createIndex({ "file_name_normalized": "text" })

// Or if using regex (current)
db.media.createIndex({ "file_name_normalized": 1 })
db.media.createIndex({ "file_name": 1 })

// Type filter
db.media.createIndex({ "file_type": 1 })
```

### Users Collection
```javascript
db.users.createIndex({ "id": 1 }, { unique: true })
```

### Groups Collection
```javascript
db.groups.createIndex({ "id": 1 }, { unique: true })
```

---

## Statistics

| Collection | Operations |
|------------|------------|
| Media | READ (90%), WRITE (10%) |
| Users | READ (80%), WRITE (20%) |
| Groups | READ (70%), WRITE (30%) |
| Connections | READ (60%), WRITE (40%) |
| Filters | READ (85%), WRITE (15%) |
