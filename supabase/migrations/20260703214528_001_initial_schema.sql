/*
# CINE3600 Admin Dashboard Initial Schema

This migration creates the core tables for the CINE3600 Telegram media indexing admin dashboard.

## Tables Created:

1. `media` - Stores indexed files from Telegram channels
   - id (uuid, primary key)
   - file_id (text, unique) - Telegram file identifier
   - file_name (text) - Original file name
   - file_size (bigint) - File size in bytes
   - file_type (text) - Type of file (video, audio, document, etc.)
   - mime_type (text) - MIME type
   - caption (text) - File caption
   - channel_id (text) - Source channel ID
   - message_id (bigint) - Telegram message ID
   - created_at (timestamptz)

2. `users` - Bot users
   - id (bigint, primary key) - Telegram user ID
   - name (text) - User display name
   - username (text) - Telegram username
   - is_banned (boolean) - Ban status
   - ban_reason (text) - Reason for ban
   - is_premium (boolean) - Premium status
   - premium_expiry (timestamptz) - Premium expiry date
   - has_free_trial (boolean) - Free trial status
   - created_at (timestamptz)

3. `groups` - Connected groups/chats
   - id (bigint, primary key) - Telegram group ID
   - title (text) - Group title
   - is_disabled (boolean) - Disabled status
   - disable_reason (text) - Reason for disabling
   - settings (jsonb) - Group settings
   - shortlink_url (text) - Shortlink domain
   - shortlink_api (text) - Shortlink API key
   - is_shortlink_enabled (boolean) - Shortlink status
   - tutorial_link (text) - Tutorial link
   - created_at (timestamptz)

4. `channels` - Indexing channels
   - id (bigint, primary key) - Telegram channel ID
   - title (text) - Channel title
   - username (text) - Channel username
   - is_active (boolean) - Active status
   - files_count (bigint) - Number of indexed files
   - last_indexed_at (timestamptz)
   - created_at (timestamptz)

5. `filters` - Group filter keywords
   - id (uuid, primary key)
   - group_id (bigint) - Group ID
   - keyword (text) - Filter keyword
   - response (text) - Filter response
   - created_at (timestamptz)

6. `logs` - Bot activity logs
   - id (uuid, primary key)
   - level (text) - Log level (info, warning, error)
   - message (text) - Log message
   - metadata (jsonb) - Additional data
   - created_at (timestamptz)

7. `stats` - Daily statistics
   - id (uuid, primary key)
   - date (date) - Stats date
   - total_users (bigint)
   - new_users (bigint)
   - total_groups (bigint)
   - new_groups (bigint)
   - total_files (bigint)
   - new_files (bigint)
   - searches (bigint) - Number of searches
   - downloads (bigint) - Number of downloads
   - created_at (timestamptz)

## Security:
- RLS enabled on all tables
- Public read/write access since this is a single-tenant admin dashboard
*/

-- Media table for indexed files
CREATE TABLE IF NOT EXISTS media (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    file_id text UNIQUE NOT NULL,
    file_name text NOT NULL,
    file_size bigint NOT NULL,
    file_type text,
    mime_type text,
    caption text,
    channel_id text,
    message_id bigint,
    created_at timestamptz DEFAULT now()
);

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id bigint PRIMARY KEY,
    name text,
    username text,
    is_banned boolean DEFAULT false,
    ban_reason text DEFAULT '',
    is_premium boolean DEFAULT false,
    premium_expiry timestamptz,
    has_free_trial boolean DEFAULT false,
    created_at timestamptz DEFAULT now()
);

-- Groups table
CREATE TABLE IF NOT EXISTS groups (
    id bigint PRIMARY KEY,
    title text,
    is_disabled boolean DEFAULT false,
    disable_reason text DEFAULT '',
    settings jsonb DEFAULT '{}',
    shortlink_url text,
    shortlink_api text,
    is_shortlink_enabled boolean DEFAULT false,
    tutorial_link text,
    created_at timestamptz DEFAULT now()
);

-- Channels table
CREATE TABLE IF NOT EXISTS channels (
    id bigint PRIMARY KEY,
    title text,
    username text,
    is_active boolean DEFAULT true,
    files_count bigint DEFAULT 0,
    last_indexed_at timestamptz,
    created_at timestamptz DEFAULT now()
);

-- Filters table
CREATE TABLE IF NOT EXISTS filters (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    group_id bigint REFERENCES groups(id) ON DELETE CASCADE,
    keyword text NOT NULL,
    response text,
    created_at timestamptz DEFAULT now()
);

-- Logs table
CREATE TABLE IF NOT EXISTS logs (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    level text NOT NULL DEFAULT 'info',
    message text NOT NULL,
    metadata jsonb DEFAULT '{}',
    created_at timestamptz DEFAULT now()
);

-- Stats table
CREATE TABLE IF NOT EXISTS stats (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    date date NOT NULL UNIQUE,
    total_users bigint DEFAULT 0,
    new_users bigint DEFAULT 0,
    total_groups bigint DEFAULT 0,
    new_groups bigint DEFAULT 0,
    total_files bigint DEFAULT 0,
    new_files bigint DEFAULT 0,
    searches bigint DEFAULT 0,
    downloads bigint DEFAULT 0,
    created_at timestamptz DEFAULT now()
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_media_file_name ON media(file_name);
CREATE INDEX IF NOT EXISTS idx_media_channel_id ON media(channel_id);
CREATE INDEX IF NOT EXISTS idx_media_created_at ON media(created_at);
CREATE INDEX IF NOT EXISTS idx_users_is_premium ON users(is_premium);
CREATE INDEX IF NOT EXISTS idx_users_is_banned ON users(is_banned);
CREATE INDEX IF NOT EXISTS idx_groups_is_disabled ON groups(is_disabled);
CREATE INDEX IF NOT EXISTS idx_logs_created_at ON logs(created_at);
CREATE INDEX IF NOT EXISTS idx_logs_level ON logs(level);
CREATE INDEX IF NOT EXISTS idx_stats_date ON stats(date);

-- Enable RLS on all tables
ALTER TABLE media ENABLE ROW LEVEL SECURITY;
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE groups ENABLE ROW LEVEL SECURITY;
ALTER TABLE channels ENABLE ROW LEVEL SECURITY;
ALTER TABLE filters ENABLE ROW LEVEL SECURITY;
ALTER TABLE logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE stats ENABLE ROW LEVEL SECURITY;

-- Media policies
DROP POLICY IF EXISTS "anon_select_media" ON media;
CREATE POLICY "anon_select_media" ON media FOR SELECT
    TO anon, authenticated USING (true);

DROP POLICY IF EXISTS "anon_insert_media" ON media;
CREATE POLICY "anon_insert_media" ON media FOR INSERT
    TO anon, authenticated WITH CHECK (true);

DROP POLICY IF EXISTS "anon_update_media" ON media;
CREATE POLICY "anon_update_media" ON media FOR UPDATE
    TO anon, authenticated USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "anon_delete_media" ON media;
CREATE POLICY "anon_delete_media" ON media FOR DELETE
    TO anon, authenticated USING (true);

-- Users policies
DROP POLICY IF EXISTS "anon_select_users" ON users;
CREATE POLICY "anon_select_users" ON users FOR SELECT
    TO anon, authenticated USING (true);

DROP POLICY IF EXISTS "anon_insert_users" ON users;
CREATE POLICY "anon_insert_users" ON users FOR INSERT
    TO anon, authenticated WITH CHECK (true);

DROP POLICY IF EXISTS "anon_update_users" ON users;
CREATE POLICY "anon_update_users" ON users FOR UPDATE
    TO anon, authenticated USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "anon_delete_users" ON users;
CREATE POLICY "anon_delete_users" ON users FOR DELETE
    TO anon, authenticated USING (true);

-- Groups policies
DROP POLICY IF EXISTS "anon_select_groups" ON groups;
CREATE POLICY "anon_select_groups" ON groups FOR SELECT
    TO anon, authenticated USING (true);

DROP POLICY IF EXISTS "anon_insert_groups" ON groups;
CREATE POLICY "anon_insert_groups" ON groups FOR INSERT
    TO anon, authenticated WITH CHECK (true);

DROP POLICY IF EXISTS "anon_update_groups" ON groups;
CREATE POLICY "anon_update_groups" ON groups FOR UPDATE
    TO anon, authenticated USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "anon_delete_groups" ON groups;
CREATE POLICY "anon_delete_groups" ON groups FOR DELETE
    TO anon, authenticated USING (true);

-- Channels policies
DROP POLICY IF EXISTS "anon_select_channels" ON channels;
CREATE POLICY "anon_select_channels" ON channels FOR SELECT
    TO anon, authenticated USING (true);

DROP POLICY IF EXISTS "anon_insert_channels" ON channels;
CREATE POLICY "anon_insert_channels" ON channels FOR INSERT
    TO anon, authenticated WITH CHECK (true);

DROP POLICY IF EXISTS "anon_update_channels" ON channels;
CREATE POLICY "anon_update_channels" ON channels FOR UPDATE
    TO anon, authenticated USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "anon_delete_channels" ON channels;
CREATE POLICY "anon_delete_channels" ON channels FOR DELETE
    TO anon, authenticated USING (true);

-- Filters policies
DROP POLICY IF EXISTS "anon_select_filters" ON filters;
CREATE POLICY "anon_select_filters" ON filters FOR SELECT
    TO anon, authenticated USING (true);

DROP POLICY IF EXISTS "anon_insert_filters" ON filters;
CREATE POLICY "anon_insert_filters" ON filters FOR INSERT
    TO anon, authenticated WITH CHECK (true);

DROP POLICY IF EXISTS "anon_update_filters" ON filters;
CREATE POLICY "anon_update_filters" ON filters FOR UPDATE
    TO anon, authenticated USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "anon_delete_filters" ON filters;
CREATE POLICY "anon_delete_filters" ON filters FOR DELETE
    TO anon, authenticated USING (true);

-- Logs policies
DROP POLICY IF EXISTS "anon_select_logs" ON logs;
CREATE POLICY "anon_select_logs" ON logs FOR SELECT
    TO anon, authenticated USING (true);

DROP POLICY IF EXISTS "anon_insert_logs" ON logs;
CREATE POLICY "anon_insert_logs" ON logs FOR INSERT
    TO anon, authenticated WITH CHECK (true);

DROP POLICY IF EXISTS "anon_delete_logs" ON logs;
CREATE POLICY "anon_delete_logs" ON logs FOR DELETE
    TO anon, authenticated USING (true);

-- Stats policies
DROP POLICY IF EXISTS "anon_select_stats" ON stats;
CREATE POLICY "anon_select_stats" ON stats FOR SELECT
    TO anon, authenticated USING (true);

DROP POLICY IF EXISTS "anon_insert_stats" ON stats;
CREATE POLICY "anon_insert_stats" ON stats FOR INSERT
    TO anon, authenticated WITH CHECK (true);

DROP POLICY IF EXISTS "anon_update_stats" ON stats;
CREATE POLICY "anon_update_stats" ON stats FOR UPDATE
    TO anon, authenticated USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "anon_delete_stats" ON stats;
CREATE POLICY "anon_delete_stats" ON stats FOR DELETE
    TO anon, authenticated USING (true);