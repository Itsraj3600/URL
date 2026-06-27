# User Flow

## Overview
This document maps the complete user journey through the CINE3600 bot - from search to file delivery.

---

## Main Search Flow

```
┌─────────────┐
│    User     │
│  (Group)    │
└──────┬──────┘
       │ Types movie name
       ▼
┌─────────────┐
│   give_     │
│  filter()   │
└──────┬──────┘
       │
       ▼
┌─────────────┐     No Match
│   manual_   │ ───────────────┐
│  filters()  │                │
└──────┬──────┘                │
       │ Match?                 │
       │ No                    │
       ▼                       │
┌─────────────┐                │
│   auto_     │                │
│  filter()   │                │
└──────┬──────┘                │
       │                       │
       ▼                       │
┌─────────────┐                │
│   get_      │                │
│  search_    │                │
│  results()  │                │
└──────┬──────┘                │
       │                       │
       ▼                       │
┌─────────────┐                │
│   MongoDB   │                │
│  (Router)   │                │
└──────┬──────┘                │
       │                       │
       ▼                       │
┌─────────────┐                │
│   Results   │                │
│   Found?    │                │
└──────┬──────┘                │
       │                       │
   Yes │                   No │
       ▼                       ▼
┌─────────────┐        ┌─────────────┐
│   Build     │        │   Spell     │
│   Buttons   │        │   Check     │
└──────┬──────┘        └──────┬──────┘
       │                      │
       ▼                      ▼
┌─────────────┐        ┌─────────────┐
│   IMDB      │        │   Request   │
│   Poster    │        │   to Admin  │
└──────┬──────┘        └─────────────┘
       │
       ▼
┌─────────────┐
│   Send      │
│   Message   │
│   to Group  │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   User      │
│   Clicks    │
│   Button    │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Check     │
│   Subscribe │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Send      │
│   File to   │
│   User PM   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   User      │
│   Receives  │
│   File      │
└─────────────┘
```

---

## Detailed Flow Breakdown

### Step 1: User Input
**Location:** Group chat

**Action:** User sends any text message (2-100 characters)

**Handler:** `plugins/pm_filter.py:give_filter()` (line 42)

```python
@Client.on_message(filters.group & filters.text & filters.incoming)
async def give_filter(client, message):
    k = await manual_filters(client, message)
    if k == False:
        await auto_filter(client, message)
```

---

### Step 2: Manual Filter Check
**Function:** `manual_filters()`

**Purpose:** Check if message matches any custom filter for this group

**Database Query:**
```python
keywords = await get_filters(group_id)
# Returns list of filter keywords
```

**Flow:**
- If filter matches → Send filter response → End
- If no match → Continue to auto_filter

---

### Step 3: Auto Search
**Function:** `auto_filter()`

**Location:** `plugins/pm_filter.py:1193`

**Process:**
```python
# 1. Get message text
search = message.text
requested_movie = search.strip()

# 2. Query database
files, offset, total_results = await get_search_results(
    search.lower(),
    offset=0,
    filter=True
)

# 3. Handle results
if not files:
    # Send request to admin channel
    await client.send_message(REQ_CHANNEL, ...)
    return
```

---

### Step 4: Database Search
**Function:** `get_search_results()`

**Location:** `database/ia_filterdb.py:247`

**Process:**
```python
# 1. Check cache first
cached = _load_search_cache(chat_id, requester_id, query, file_type, filter)
if cached is None:
    # 2. Query all healthy database nodes
    files, total = await router.find_all(flt)
    # 3. Store in cache
    _store_search_cache(chat_id, requester_id, query, file_type, filter, projected, total)
```

**Database Flow:**
```
get_search_results()
       │
       ▼
   _build_filter()
       │
       ▼
   router.find_all()
       │
       ├─────────────┐
       ▼             ▼
   Primary DB   Secondary DB
   (healthy)    (healthy)
       │             │
       └──────┬──────┘
              ▼
         Merge Results
              │
              ▼
         Return Files
```

---

### Step 5: Button Generation
**Location:** `auto_filter()` in `pm_filter.py`

**Logic:**
```python
# Check URL mode and user type
if URL_MODE and user not in ADMINS:
    # Shortlink buttons
    btn = [[InlineKeyboardButton(name, url=shortlink)]]
else:
    # Direct callback buttons
    btn = [[InlineKeyboardButton(name, callback_data=f'files#{file_id}')]]

# Add pagination
btn.append([BACK, PAGE_INFO, NEXT])
```

**Button Types:**

| User Type | Button Type | Action |
|-----------|-------------|--------|
| Admin | Callback | Direct file send |
| Premium | Callback | Direct file send |
| Normal | URL Shortlink | Redirect to bot |
| Group Whitelist | Callback | Direct file send |

---

### Step 6: IMDB Metadata
**Function:** `get_poster()`

**Purpose:** Fetch movie metadata from IMDB

**Data Retrieved:**
- Title, Year, Rating
- Poster image URL
- Plot, Cast, Director
- Genres, Runtime

**Template Applied:**
```python
cap = TEMPLATE.format(
    query=search,
    title=imdb['title'],
    rating=imdb['rating'],
    ...
)
```

---

### Step 7: Message Send
**Action:** Send results to group

**Message Content:**
- IMDB poster image (if found)
- Movie metadata caption
- File buttons (paginated)

```python
await message.reply_photo(
    photo=imdb.get('poster'),
    caption=cap[:1024],
    reply_markup=InlineKeyboardMarkup(btn)
)
```

---

### Step 8: User Clicks File Button
**Callback Data:** `files#{file_id}`

**Handler:** `plugins/pm_filter.py:581`

**Flow:**
```
User clicks button
        │
        ▼
   Parse callback data
        │
        ▼
   get_file_details(file_id)
        │
        ▼
   Check subscription
        │
   ┌────┴────┐
   │         │
Subscribed  Not Subscribed
   │         │
   ▼         ▼
Send file  Redirect to PM
```

---

### Step 9: File Delivery
**Method:** `send_cached_media()`

**Process:**
```python
await client.send_cached_media(
    chat_id=query.from_user.id,
    file_id=file_id,
    caption=f_caption,
    reply_markup=stream_button,
    protect_content=True if secure else False
)
```

**User Receives:**
1. Media file (video/audio/document)
2. Caption with file info
3. Stream/Download button

---

## Inline Search Flow

```
┌─────────────┐
│    User     │
│ Types @bot  │
│   name      │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Inline    │
│   Query     │
│   Handler   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Check     │
│ Subscription│
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Search    │
│   DB        │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Return    │
│   Inline    │
│   Results   │
└─────────────┘
```

**Handler:** `plugins/inline.py:answer()`

**Process:**
```python
# Parse query
string = query.query.strip()
file_type = None

# Search
files, next_offset, total = await get_search_results(
    chat_id, string, file_type=file_type, max_results=10, offset=offset
)

# Build inline results
results = [
    InlineQueryResultCachedDocument(
        title=file.file_name,
        document_file_id=file.file_id,
        caption=f_caption
    )
    for file in files
]

await query.answer(results=results, next_offset=str(next_offset))
```

---

## Request Flow (No Results)

```
┌─────────────┐
│    User     │
│  Searches   │
│  (No Match) │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Send to   │
│   Request   │
│   Channel   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Admin     │
│   Sees      │
│   Request   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Admin     │
│   Action    │
└──────┬──────┘
       │
   ┌───┼───┬───────┬───────┐
   ▼   ▼   ▼       ▼       ▼
Upload Spell Already Not   Reject
Done Error Available Avail
   │   │   │       │       │
   └───┴───┴───────┴───────┘
           │
           ▼
┌─────────────┐
│   Notify    │
│   User      │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   User      │
│   Informed  │
└─────────────┘
```

---

## Pagination Flow

```
Page 1 (offset=0)
       │
   User clicks Next
       │
       ▼
next_12345_key1_10
       │
       ▼
get_search_results(offset=10)
       │
       ▼
Page 2 (offset=10)
       │
   User clicks Next
       │
       ▼
next_12345_key1_20
       │
       ▼
Page 3 (offset=20)
```

**Key Storage:**
```python
# Store search query for pagination
key = f"{message.chat.id}-{message.id}"
BUTTONS[key] = search_query
```

---

## Error Flows

### User Not Subscribed
```
Click button → Check subscription → Not subscribed
       │
       ▼
Redirect to bot PM with start parameter
       │
       ▼
User must join channel first
```

### User Blocked Bot
```
Try send to PM → UserIsBlocked error
       │
       ▼
Alert: "Unblock the bot"
```

### File Not Found
```
get_file_details() → Empty list
       │
       ▼
Alert: "No such file exists"
```

---

## Performance Timing

| Step | Typical Time | Bottleneck |
|------|--------------|------------|
| Manual filter check | 10-50ms | Database query |
| Auto search | 50-200ms | MongoDB query |
| Cache hit | 5-10ms | Memory lookup |
| Cache miss | 100-500ms | Multi-DB query |
| IMDB fetch | 500-2000ms | External API |
| Button generation | 1-5ms | CPU |
| Message send | 100-300ms | Telegram API |
| File send | 200-1000ms | Telegram API |

**Total Search → File Time:**
- Best case: ~400ms (cached, no IMDB)
- Typical: ~2-3 seconds (with IMDB)
- Worst case: ~5+ seconds (external API slow)

---

## Optimization Opportunities

1. **Parallel Operations:** Fetch IMDB while rendering buttons
2. **Cache IMDB Results:** Store IMDB data for popular movies
3. **Pre-compute Buttons:** Build button structure before search returns
4. **Edge Caching:** Cache results at Telegram's edge
5. **Predictive Loading:** Pre-load next page of results
