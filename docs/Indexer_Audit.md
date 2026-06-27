# Indexer Audit

## Overview
This document catalogs all indexing operations in the CINE3600 bot - the process of importing media files from Telegram channels into the database.

---

## Indexing Flow

```
User sends link/forward
        ↓
   Admin Approval
        ↓
   index_files_to_db()
        ↓
   Iterate messages
        ↓
   Extract media
        ↓
   save_file() to DB
        ↓
   Report results
```

---

## Indexing Functions

### Function: `index_files_to_db()`
**File:** `plugins/index.py:137`

**Purpose:**
Main indexing worker. Iterates through channel messages and saves media to database.

**Called By:**
- `index_files()` callback handler - line 49

**Calls:**
- `bot.iter_messages()` - iterate channel messages
- `save_file()` - save each media to database
- `msg.edit_text()` - update progress

**Parameters:**
- `lst_msg_id` - Last message ID to index from
- `chat` - Channel ID or username
- `msg` - Message to update progress
- `bot` - Pyrogram client

**Process:**
```python
# Iterate messages from channel
async for message in bot.iter_messages(chat, lst_msg_id, temp.CURRENT):
    # Skip empty messages
    if message.empty:
        deleted += 1
        continue
    
    # Skip non-media messages
    if not message.media:
        no_media += 1
        continue
    
    # Only allow VIDEO, AUDIO, DOCUMENT
    if message.media not in [VIDEO, AUDIO, DOCUMENT]:
        unsupported += 1
        continue
    
    # Extract media and save
    media.file_type = message.media.value
    media.caption = message.caption
    saved, code = await save_file(media)
    
    if saved:
        total_files += 1
    elif code == 0:
        duplicate += 1
    else:
        errors += 1
```

**Database Operations:**
- Multiple `save_file()` calls (one per media)

**Progress Updates:**
- Every 20 messages, updates the status message

**Returns:**
- None (reports results in edited message)

---

### Function: `index_files()`
**File:** `plugins/index.py:17`

**Purpose:**
Callback handler for admin approval of indexing requests.

**Trigger:**
- Callback data starting with `index`

**Calls:**
- `index_files_to_db()` - starts actual indexing

**Process:**
```python
# Parse callback data
_, raju, chat, lst_msg_id, from_user = query.data.split("#")

# Handle cancel
if query.data.startswith('index_cancel'):
    temp.CANCEL = True
    return

# Handle rejection
if raju == 'reject':
    await bot.send_message(from_user, 'Submission declined')
    return

# Accept and start indexing
await index_files_to_db(int(lst_msg_id), chat, msg, bot)
```

**Callback Data Format:**
- Accept: `index#accept#{chat_id}#{last_msg_id}#{from_user_id}`
- Reject: `index#reject#{chat_id}#{msg_id}#{from_user_id}`
- Cancel: `index_cancel`

---

### Function: `send_for_index()`
**File:** `plugins/index.py:52`

**Purpose:**
Handles incoming index requests (link or forwarded message).

**Trigger:**
- Forwarded messages from channels
- Text messages matching Telegram link pattern

**Calls:**
- `bot.get_chat()` - verify access to channel
- `bot.get_messages()` - verify last message exists
- `bot.create_chat_invite_link()` - create invite if private

**Process:**
```python
# Parse link or forwarded message
if message.text:
    # Extract chat_id and last_msg_id from URL
    regex = re.compile("(https://)?(t\.me/|telegram\.me/|)(c/)?(\d+|[a-zA-Z_0-9]+)/(\d+)$")
    # ...
    
elif message.forward_from_chat:
    # Get from forwarded message
    last_msg_id = message.forward_from_message_id
    chat_id = message.forward_from_chat.username or id

# Verify access
await bot.get_chat(chat_id)
await bot.get_messages(chat_id, last_msg_id)

# For admins: show approval buttons
if user in ADMINS:
    await message.reply('Start indexing?', reply_markup=approval_buttons)
    
# For non-admins: send to LOG_CHANNEL for moderation
else:
    await bot.send_message(LOG_CHANNEL, '#IndexRequest\n...', reply_markup=approval_buttons)
```

---

### Function: `save_file(media)`
**File:** `database/ia_filterdb.py:187`

**Purpose:**
Save media metadata to database.

**Called By:**
- `index_files_to_db()` - during indexing

**Process:**
```python
# Extract and encode file_id
file_id, file_ref = unpack_new_file_id(media.file_id)

# Normalize filename
file_name = re.sub(r"(_|\-|\.|\+)", " ", str(media.file_name))

# Build document
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

# Save via router (load-balanced)
saved, code = await router.save_file(doc)
```

**Returns:**
- `(True, 1)` - saved successfully
- `(False, 0)` - duplicate (already exists)
- `(False, 2)` - error

---

### Function: `set_skip_number()`
**File:** `plugins/index.py:123`

**Purpose:**
Set number of messages to skip when resuming indexing.

**Trigger:**
- `/setskip {number}` command (admin only)

**Usage:**
```
/setskip 100  # Skip first 100 messages
```

---

## Duplicate Detection

### Method: Insert-First Pattern
The system uses MongoDB's unique `_id` index for duplicate detection:

```python
try:
    await node.media.insert_one(doc)
    return True, 1  # Saved
except DuplicateKeyError:
    return False, 0  # Duplicate
```

**Key:** `_id` field = encoded Telegram file_id

This means:
- Same file_id cannot be stored twice
- Re-indexing same channel is safe (duplicates skipped)
- No pre-check needed (faster for new files)

---

## Index Start

**Entry Points:**
1. Forward message from channel → `send_for_index()`
2. Send Telegram link → `send_for_index()`
3. Admin uses approval button → `index_files()`

**Prerequisites:**
- Bot must be admin in target channel
- Bot must have access to channel messages
- Channel must contain media (video/audio/document)

---

## Index Resume

**Mechanism:**
- `temp.CURRENT` stores skip count
- Set via `/setskip {number}`
- Used in `iter_messages(chat, lst_msg_id, temp.CURRENT)`

**Usage:**
```python
# Skip first X messages (already indexed)
temp.CURRENT = skip_number

# Then start indexing
await index_files_to_db(lst_msg_id, chat, msg, bot)
```

---

## Bulk Insert

**Current Approach:**
- Sequential processing (one at a time)
- Progress updates every 20 messages
- No batch insert

**Performance:**
- Slow for large channels
- Each file requires:
  1. Extract media data
  2. Build document
  3. Database insert
  4. Update progress

**Potential Optimization:**
- Batch inserts (100 at a time)
- Parallel processing
- Skip progress updates for faster indexing

---

## Auto Index

**Not Implemented**

Currently indexing is manual only. No automatic detection of new messages in indexed channels.

**Potential Feature:**
- Watch channel for new messages
- Auto-save new media
- Would require channel monitoring worker

---

## Delete Operations

### `delete_file(query)` - `database/router.py:122`
**Purpose:** Delete from ALL nodes
```python
for node in healthy_nodes():
    result = await node.media.delete_many(query)
    deleted += result.deleted_count
return deleted
```

### `delete_one(query)` - `database/router.py:137`
**Purpose:** Delete single file
```python
for node in healthy_nodes():
    result = await node.media.delete_one(query)
    if result.deleted_count:
        return result.deleted_count
return 0
```

---

## Update Operations

**Not Implemented**

Current system does not support updating existing file metadata. To update:
1. Delete existing file
2. Re-index the file

**File Fields That Cannot Change:**
- `_id` (file_id) - immutable
- `file_ref` - may expire, needs refresh

---

## Cancel Indexing

**Mechanism:**
```python
# Set cancel flag
temp.CANCEL = True

# Check in indexing loop
if temp.CANCEL:
    await msg.edit(f"Cancelled! Saved {total_files} files...")
    break
```

**Trigger:** `index_cancel` callback button

---

## Indexing Statistics Tracking

The indexer tracks:
- `total_files` - Successfully saved
- `duplicate` - Skipped (already exists)
- `deleted` - Deleted messages in channel
- `no_media` - Non-media messages
- `unsupported` - Unsupported media types (photos, stickers, etc.)
- `errors` - Failed saves

**Final Report:**
```
Successfully saved {total_files} to database!
Duplicate Files Skipped: {duplicate}
Deleted Messages Skipped: {deleted}
Non-Media messages skipped: {no_media + unsupported}
(Unsupported Media - {unsupported})
Errors Occurred: {errors}
```

---

## Supported Media Types

| Type | Supported |
|------|-----------|
| Video | Yes |
| Audio | Yes |
| Document | Yes |
| Photo | No |
| Sticker | No |
| Animation (GIF) | No |
| Voice | No |
| Video Note | No |

---

## Performance Metrics

For a channel with 10,000 messages:
- Expected duplicates: ~5-10%
- Expected non-media: Varies by channel
- Processing time: ~1-2 seconds per file
- Total time: ~3-6 hours

**Bottlenecks:**
1. Telegram API rate limits
2. Sequential processing
3. Progress message updates

---

## Recommendations

1. **Add batch processing** - Insert 100 files at once
2. **Parallel indexing** - Use multiple workers
3. **Reduce progress updates** - Every 100 instead of 20
4. **Add text index** - Speed up `file_name_normalized` searches
5. **Consider auto-index** - Watch channels for new content
