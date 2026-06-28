'use client'

import { useState, useEffect } from 'react'
import Card from '@/app/(dashboard)/components/Card'
import StatCard from '@/app/(dashboard)/components/StatCard'
import ProgressBar from '@/app/(dashboard)/components/ProgressBar'

interface OverviewStats {
  bot_status: string
  uptime_seconds: number
  total_users: number
  total_files: number
  total_channels: number
  searches_today: number
  downloads_today: number
  cache_hit_rate: number
  avg_search_time_ms: number
  indexing_status: string
  indexing_progress: number
  db_status: string
}

export default function DashboardOverview() {
  const [stats, setStats] = useState<OverviewStats | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Mock data for now - would fetch from API
    const mockStats: OverviewStats = {
      bot_status: 'online',
      uptime_seconds: 86400,
      total_users: 18432,
      total_files: 492318,
      total_channels: 27,
      searches_today: 52117,
      downloads_today: 13921,
      cache_hit_rate: 93.2,
      avg_search_time_ms: 45,
      indexing_status: 'running',
      indexing_progress: 74,
      db_status: 'healthy'
    }

    setTimeout(() => {
      setStats(mockStats)
      setLoading(false)
    }, 500)
  }, [])

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Dashboard Overview</h1>
          <p className="text-zinc-400">Real-time monitoring and statistics</p>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
          <span className="text-sm text-zinc-400">Live</span>
        </div>
      </div>

      {/* Status Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Bot Status"
          value={stats?.bot_status || 'offline'}
          icon="🤖"
          status={stats?.bot_status === 'online' ? 'success' : 'danger'}
        />
        <StatCard
          title="Users"
          value={stats?.total_users?.toLocaleString() || '0'}
          icon="👥"
          trend="+184 today"
        />
        <StatCard
          title="Total Files"
          value={stats?.total_files?.toLocaleString() || '0'}
          icon="📁"
        />
        <StatCard
          title="Channels"
          value={stats?.total_channels?.toString() || '0'}
          icon="📡"
        />
      </div>

      {/* Activity Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <StatCard
          title="Today's Searches"
          value={stats?.searches_today?.toLocaleString() || '0'}
          icon="🔍"
          trend="+12%"
        />
        <StatCard
          title="Today's Downloads"
          value={stats?.downloads_today?.toLocaleString() || '0'}
          icon="⬇️"
          trend="+8%"
        />
        <StatCard
          title="Cache Hit Rate"
          value={`${stats?.cache_hit_rate || 0}%`}
          icon="⚡"
          status="success"
        />
      </div>

      {/* Indexing Progress */}
      <Card title="Indexing Status" icon="📝">
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-zinc-400">Status</span>
            <span className={`px-2 py-1 rounded text-sm ${
              stats?.indexing_status === 'running'
                ? 'bg-blue-500/20 text-blue-400'
                : 'bg-zinc-700 text-zinc-400'
            }`}>
              {stats?.indexing_status || 'idle'}
            </span>
          </div>
          {stats?.indexing_status === 'running' && (
            <>
              <ProgressBar value={stats?.indexing_progress || 0} />
              <div className="grid grid-cols-3 gap-4 text-sm">
                <div>
                  <span className="text-zinc-500">Processed</span>
                  <p className="font-mono text-lg">45,218</p>
                </div>
                <div>
                  <span className="text-zinc-500">Inserted</span>
                  <p className="font-mono text-lg">44,892</p>
                </div>
                <div>
                  <span className="text-zinc-500">Speed</span>
                  <p className="font-mono text-lg">145 f/s</p>
                </div>
              </div>
            </>
          )}
        </div>
      </Card>

      {/* System Status */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card title="Database" icon="🗄️">
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-zinc-400">Status</span>
              <span className="flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-green-500" />
                <span className="text-green-400">{stats?.db_status}</span>
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-zinc-400">Size</span>
              <span className="font-mono">485.2 MB</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-zinc-400">Collections</span>
              <span className="font-mono">7</span>
            </div>
          </div>
        </Card>

        <Card title="Performance" icon="⚡">
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-zinc-400">Avg Search Time</span>
              <span className="font-mono">{stats?.avg_search_time_ms} ms</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-zinc-400">Uptime</span>
              <span className="font-mono">24h 0m</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-zinc-400">Workers</span>
              <span className="font-mono">8/8 active</span>
            </div>
          </div>
        </Card>
      </div>

      {/* Live Activity Feed */}
      <Card title="Live Activity" icon="🔥">
        <div className="space-y-3 max-h-64 overflow-y-auto">
          {[
            { time: '12:35', event: 'User searched "Interstellar"', type: 'search' },
            { time: '12:34', event: 'Worker #3 completed batch of 500', type: 'index' },
            { time: '12:33', event: 'Duplicate file skipped', type: 'skip' },
            { time: '12:32', event: 'New user joined', type: 'user' },
            { time: '12:31', event: 'Cache hit for "matrix"', type: 'cache' },
          ].map((activity, i) => (
            <div key={i} className="flex items-center gap-3 text-sm">
              <span className="text-zinc-500 w-12">{activity.time}</span>
              <span className={`w-2 h-2 rounded-full ${
                activity.type === 'search' ? 'bg-blue-500' :
                activity.type === 'index' ? 'bg-green-500' :
                activity.type === 'user' ? 'bg-purple-500' :
                activity.type === 'cache' ? 'bg-yellow-500' :
                'bg-zinc-500'
              }`} />
              <span className="text-zinc-300">{activity.event}</span>
            </div>
          ))}
        </div>
      </Card>
    </div>
  )
}
