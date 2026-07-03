import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!

export const supabase = createClient(supabaseUrl, supabaseAnonKey)

// Type definitions for database tables
export type Media = {
  id: string
  file_id: string
  file_name: string
  file_size: number
  file_type: string | null
  mime_type: string | null
  caption: string | null
  channel_id: string | null
  message_id: number | null
  created_at: string
}

export type User = {
  id: number
  name: string | null
  username: string | null
  is_banned: boolean
  ban_reason: string
  is_premium: boolean
  premium_expiry: string | null
  has_free_trial: boolean
  created_at: string
}

export type Group = {
  id: number
  title: string | null
  is_disabled: boolean
  disable_reason: string
  settings: Record<string, unknown>
  shortlink_url: string | null
  shortlink_api: string | null
  is_shortlink_enabled: boolean
  tutorial_link: string | null
  created_at: string
}

export type Channel = {
  id: number
  title: string | null
  username: string | null
  is_active: boolean
  files_count: number
  last_indexed_at: string | null
  created_at: string
}

export type Filter = {
  id: string
  group_id: number
  keyword: string
  response: string | null
  created_at: string
}

export type Log = {
  id: string
  level: 'info' | 'warning' | 'error'
  message: string
  metadata: Record<string, unknown>
  created_at: string
}

export type Stats = {
  id: string
  date: string
  total_users: number
  new_users: number
  total_groups: number
  new_groups: number
  total_files: number
  new_files: number
  searches: number
  downloads: number
  created_at: string
}
