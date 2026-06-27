# Callback Audit

## Overview
This document catalogs all callback query handlers in the CINE3600 bot.

---

## Callback Handler Function

### `cb_handler()`
**File:** `plugins/pm_filter.py:391`

**Trigger:** All callback queries (catch-all handler)

**Structure:**
```python
@Client.on_callback_query()
async def cb_handler(client: Client, query: CallbackQuery):
    data = query.data
    # Match on data string...
```

---

## Callback Types

### 1. Search Button - `files#{file_id}`

**Pattern:** `files#.*`

**Purpose:** User clicks on a movie/file button in search results

**Handler Location:** `pm_filter.py:581-627`

**Process:**
```python
ident, file_id = query.data.split("#")
files_ = await get_file_details(file_id)

# Check subscription
if AUTH_CHANNEL and not await is_subscribed(client, query):
    await query.answer(url=f"https://t.me/{bot}?start={ident}_{file_id}")
    return

# Check bot PM setting
if settings['botpm']:
    await query.answer(url=f"https://t.me/{bot}?start={ident}_{file_id}")
    return

# Send file to user's PM
await client.send_cached_media(
    chat_id=query.from_user.id,
    file_id=file_id,
    caption=f_caption,
    reply_markup=generate_stream_button
)
```

**Database Queries:**
- `get_file_details(file_id)` - Fetch file metadata
- `get_settings(chat_id)` - Get group settings

**User Experience:**
1. User sees search results with file buttons
2. Clicks button → File sent to PM
3. Or redirected to bot PM if not subscribed

---

### 2. Next Page - `next_{req}_{key}_{offset}`

**Pattern:** `^next`

**Purpose:** Pagination through search results

**Handler Location:** `pm_filter.py:149-364`

**Process:**
```python
ident, req, key, offset = query.data.split("_")
search = BUTTONS.get(key)

# Get next page
files, n_offset, total = await get_search_results(search, offset=offset, filter=True)

# Build buttons based on user type and settings
if URL_MODE and user not in ADMINS/MY_USERS:
    # Shortlink buttons
    btn = [[InlineKeyboardButton(name, url=shortlink)]]
else:
    # Direct callback buttons
    btn = [[InlineKeyboardButton(name, callback_data=f'files#{file_id}')]]

# Add pagination buttons
btn.append([BACK, PAGE_INFO, NEXT])
```

**Database Queries:**
- `get_search_results()` - Fetch next page
- `get_settings()` - Get button style

**User Experience:**
1. User clicks "NEXT"
2. Message updates with new file buttons
3. Pagination info shows "Page X/Y"

---

### 3. Previous Page - `next_{req}_{key}_{offset}`

**Pattern:** `^next` (same as Next, with lower offset)

**Purpose:** Go back to previous search results page

**Handler Location:** `pm_filter.py:149-364`

**Process:**
```python
# Same as next page, but with offset-10
if 0 < offset <= 10:
    off_set = 0
elif offset == 0:
    off_set = None  # No back button
else:
    off_set = offset - 10
```

---

### 4. Movie Button (Spell Check) - `spolling#{user}#{movie_index}`

**Pattern:** `^spolling`

**Purpose:** Handle click on spell check suggestion

**Handler Location:** `pm_filter.py:367-388`

**Process:**
```python
_, user, movie_ = query.data.split("#")

# Get suggestions list
movies = SPELL_CHECK.get(query.message.reply_to_message.id)
movie = movies[int(movie_)]

# Search for suggested movie
files, offset, total = await get_search_results(movie, offset=0, filter=True)

if files:
    await auto_filter(bot, query, (movie, files, offset, total))
else:
    await query.message.edit('Currently unavailable!')
```

**User Experience:**
1. User misspells movie name
2. Bot shows "Did you mean..." suggestions
3. User clicks suggestion
4. Bot searches for correct spelling

---

### 5. Delete Button - `close_data`

**Pattern:** `close_data`

**Purpose:** Close/delete a message

**Handler Location:** `pm_filter.py:394`

**Process:**
```python
if query.data == "close_data":
    await query.message.delete()
```

---

### 6. Delete All Confirm - `delallconfirm`

**Pattern:** `delallconfirm`

**Purpose:** Confirm deletion of all filters in group

**Handler Location:** `pm_filter.py:396-428`

**Process:**
```python
# Check ownership
st = await client.get_chat_member(grp_id, userid)
if st.status == OWNER or userid in ADMINS:
    await del_all(query.message, grp_id, title)
```

**Database Queries:**
- `del_all()` - Drops filter collection

---

### 7. Delete All Cancel - `delallcancel`

**Pattern:** `delallcancel`

**Purpose:** Cancel deletion of all filters

**Handler Location:** `pm_filter.py:429-447`

**Process:**
```python
await query.message.delete()
await query.message.reply_to_message.delete()
```

---

### 8. Group Connection Callbacks - `groupcb:{group_id}:{status}`

**Pattern:** `groupcb:`

**Purpose:** Show group details in connection management

**Handler Location:** `pm_filter.py:448-476`

**Process:**
```python
group_id = query.data.split(":")[1]
act = query.data.split(":")[2]

stat = "CONNECT" if act == "" else "DISCONNECT"
keyboard = [[CONNECT/DISCONNECT, DELETE], [BACK]]
await query.message.edit_text(f"Group: {title}\nID: {group_id}", reply_markup=keyboard)
```

---

### 9. Connect Callback - `connectcb:{group_id}`

**Pattern:** `connectcb:`

**Purpose:** Connect user to a group

**Handler Location:** `pm_filter.py:477-497`

**Process:**
```python
group_id = query.data.split(":")[1]
mkact = await make_active(str(user_id), str(group_id))
await query.message.edit_text(f"Connected to {title}")
```

**Database Queries:**
- `make_active()` - Update connection

---

### 10. Disconnect Callback - `disconnect:{group_id}`

**Pattern:** `disconnect:`

**Purpose:** Disconnect user from a group

**Handler Location:** `pm_filter.py:498-520`

**Process:**
```python
group_id = query.data.split(":")[1]
mkinact = await make_inactive(str(user_id))
await query.message.edit_text(f"Disconnected from {title}")
```

**Database Queries:**
- `make_inactive()` - Update connection

---

### 11. Delete Connection - `deletecb:{group_id}`

**Pattern:** `deletecb:`

**Purpose:** Delete a group connection

**Handler Location:** `pm_filter.py:521-538`

**Process:**
```python
group_id = query.data.split(":")[1]
delcon = await delete_connection(str(user_id), str(group_id))
await query.message.edit_text("Successfully deleted connection")
```

**Database Queries:**
- `delete_connection()` - Remove connection

---

### 12. Back Callback - `backcb`

**Pattern:** `backcb`

**Purpose:** Go back to connections list

**Handler Location:** `pm_filter.py:539-570`

**Process:**
```python
groupids = await all_connections(str(userid))
buttons = [[InlineKeyboardButton(f"{title}{act}", callback_data=f"groupcb:{groupid}:{act}")]
           for groupid in groupids]
await query.message.edit_text("Your connections:", reply_markup=buttons)
```

**Database Queries:**
- `all_connections()` - Get user's connections

---

### 13. Alert Message - `alertmessage:{index}:{keyword}`

**Pattern:** `alertmessage`

**Purpose:** Show alert message for filter button

**Handler Location:** `pm_filter.py:571-580`

**Process:**
```python
i = query.data.split(":")[1]
keyword = query.data.split(":")[2]
reply_text, btn, alerts, fileid = await find_filter(grp_id, keyword)
alert = alerts[int(i)]
await query.answer(alert, show_alert=True)
```

**Database Queries:**
- `find_filter()` - Get filter content

---

### 14. Generate Stream Link - `generate_stream_link:{file_id}`

**Pattern:** `generate_stream_link`

**Purpose:** Generate web stream/download link

**Handler Location:** `pm_filter.py:757-792`

**Process:**
```python
_, file_id = data.split(":")

# Send to log channel
log_msg = await client.send_cached_media(chat_id=LOG_CHANNEL, file_id=file_id)

# Generate URLs
lazy_stream = f"{URL}watch/{log_msg.id}/{file_name}?hash={hash}"
lazy_download = f"{URL}{log_msg.id}/{file_name}?hash={hash}"

# Send to user
await query.message.reply_text("Link generated!", reply_markup=[web_download, stream])
```

---

### 15. Notify User Callbacks

**Patterns:**
- `notify_user_not_avail:{user_id}:{movie}`
- `notify_user_alrupl:{user_id}:{movie}`
- `notify_userupl:{user_id}:{movie}`
- `notify_user_req_rejected:{user_id}:{movie}`
- `notify_user_spelling_error:{user_id}:{movie}`
- `notify_user_custom:{user_id}:{movie}`
- `notify_user_req_rcvd:{user_id}:{movie}`

**Purpose:** Admin actions for content requests

**Handler Location:** `pm_filter.py:795-989`

**Process:**
```python
_, user_id, movie = data.split(":")

# Send notification to user
await client.send_message(int(user_id), f"Status: {status}")

# Update admin log
await query.edit_message_text(f"User notified. Status: {status}")
```

---

### 16. Settings Callbacks - `setgs#{setting}#{status}#{grp_id}`

**Pattern:** `setgs`

**Purpose:** Toggle group settings

**Handler Location:** `pm_filter.py:1101-1191`

**Process:**
```python
ident, set_type, status, grp_id = query.data.split("#")

# Toggle setting
if status == "True":
    await save_group_settings(grpid, set_type, False)
else:
    await save_group_settings(grpid, set_type, True)

# Update button text
settings = await get_settings(grpid)
# Edit message with new buttons
```

**Available Settings:**
- `button` - Filter button (single/double)
- `botpm` - Send to bot PM
- `file_secure` - Protect content
- `imdb` - IMDB template
- `spell_check` - Spell check
- `welcome` - Welcome message

---

### 17. Help Navigation Callbacks

**Patterns:**
- `start` - Home screen
- `help` - Help menu
- `about` - About page
- `manuelfilter` - Manual filter help
- `autofilter` - Auto filter help
- `button` - Button help
- `coct` - Connection help
- `extra` - Extra features
- `admin` - Admin help
- `stats` - Bot statistics
- `rfrsh` - Refresh stats
- `source` - Source code

**Purpose:** Navigate help menus

**Handler Location:** `pm_filter.py:664-755, 991-1069`

---

### 18. Index Callbacks - `index#*`

**Pattern:** `^index`

**Purpose:** Handle indexing approvals/rejections

**Handler Location:** `plugins/index.py:17-49`

**Patterns:**
- `index#accept#{chat}#{msg_id}#{user}` - Accept index
- `index#reject#{chat}#{msg_id}#{user}` - Reject index
- `index_cancel` - Cancel ongoing index

---

## Callback Data Format Summary

| Callback | Format | Example |
|----------|--------|---------|
| File | `files#{file_id}` | `files#AgAC...` |
| Next Page | `next_{req}_{key}_{offset}` | `next_12345_msg1_10` |
| Spell Check | `spolling#{user}#{index}` | `spolling#12345#2` |
| Settings | `setgs#{type}#{status}#{grp}` | `setgs#button#True#-100` |
| Connection | `connectcb:{group_id}` | `connectcb:-100123456` |
| Notify | `notify_user_{status}:{uid}:{movie}` | `notify_userupl:12345:Avatar` |
| Index | `index#{action}#{chat}#{msg}#{user}` | `index#accept#-100#500#12345` |

---

## Performance Notes

1. All handlers check user permissions before acting
2. Admin-only callbacks verify `ADMINS` list
3. Owner-only callbacks check chat member status
4. Pagination uses cached search results when possible
5. File sends use `send_cached_media` for efficiency
