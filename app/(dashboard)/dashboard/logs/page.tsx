'use client'

import { useState, useEffect, useRef } from 'react'
import Card from '@/app/(dashboard)/components/Card'

type LogLevel = 'INFO' | 'WARNING' | 'ERROR' | 'DEBUG'

interface LogEntry {
  time: string
  level: LogLevel
  message: string
  source: string
}

const mockLogs: LogEntry[] = [
  { time: '12:35:01', level: 'INFO', message: 'Connected to MongoDB Primary', source: 'db' },
  { time: '12:35:00', level: 'INFO', message: 'Worker #3 started', source: 'worker' },
  { time: '12:34:58', level: 'DEBUG', message: 'Cache hit for query: avatar', source: 'cache' },
  { time: '12:34:55', level: 'INFO', message: 'Bulk write completed: 500 documents', source: 'index' },
  { time: '12:34:52', level: 'WARNING', message: 'Retrying Telegram API (FloodWait)', source: 'api' },
  { time: '12:34:50', level: 'ERROR', message: 'Duplicate key error: file_abc123', source: 'db' },
  { time: '12:34:48', level: 'INFO', message: 'User searched: Interstellar', source: 'search' },
  { time: '12:34:45', level: 'DEBUG', message: 'Normalized query: the matrix 1999', source: 'search' },
  { time: '12:34:42', level: 'INFO', message: 'File sent to user 123456789', source: 'bot' },
  { time: '12:34:40', level: 'WARNING', message: 'Cache miss for query: oppenheimer', source: 'cache' },
]

export default function LogsPage() {
  const [logs, setLogs] = useState<LogEntry[]>(mockLogs)
  const [filter, setFilter] = useState<LogLevel | 'ALL'>('ALL')
  const [search, setSearch] = useState('')
  const [autoScroll, setAutoScroll] = useState(true)
  const logEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (autoScroll) {
      logEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    }
  }, [logs, autoScroll])

  const levelColors: Record<LogLevel, string> = {
    INFO: 'bg-blue-500/20 text-blue-400',
    WARNING: 'bg-yellow-500/20 text-yellow-400',
    ERROR: 'bg-red-500/20 text-red-400',
    DEBUG: 'bg-zinc-700 text-zinc-400',
  }

  const filteredLogs = logs.filter((log) => {
    if (filter !== 'ALL' && log.level !== filter) return false
    if (search && !log.message.toLowerCase().includes(search.toLowerCase())) return false
    return true
  })

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Log Viewer</h1>
          <p className="text-zinc-400">Real-time log monitoring</p>
        </div>
        <div className="flex items-center gap-4">
          <label className="flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={autoScroll}
              onChange={(e) => setAutoScroll(e.target.checked)}
              className="rounded border-zinc-700"
            />
            Auto-scroll
          </label>
          <button className="px-3 py-1 bg-zinc-700 text-zinc-300 rounded text-sm hover:bg-zinc-600">
            Download Logs
          </button>
        </div>
      </div>

      {/* Filters */}
      <Card>
        <div className="flex flex-wrap items-center gap-4">
          {/* Search */}
          <div className="flex-1 min-w-[200px]">
            <input
              type="text"
              placeholder="Search logs..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full px-4 py-2 bg-zinc-800 border border-zinc-700 rounded-lg text-sm focus:outline-none focus:border-blue-500"
            />
          </div>

          {/* Level filters */}
          <div className="flex items-center gap-2">
            {['ALL', 'INFO', 'WARNING', 'ERROR', 'DEBUG'].map((level) => (
              <button
                key={level}
                onClick={() => setFilter(level as LogLevel | 'ALL')}
                className={`px-3 py-1 rounded text-sm transition-colors ${
                  filter === level
                    ? 'bg-blue-600 text-white'
                    : 'bg-zinc-800 text-zinc-400 hover:bg-zinc-700'
                }`}
              >
                {level}
              </button>
            ))}
          </div>
        </div>
      </Card>

      {/* Log Stream */}
      <Card>
        <div className="bg-zinc-950 rounded-lg p-4 font-mono text-sm h-[600px] overflow-y-auto">
          {filteredLogs.map((log, i) => (
            <div key={i} className="flex items-start gap-3 py-1 hover:bg-zinc-900/50">
              <span className="text-zinc-500 w-20 flex-shrink-0">{log.time}</span>
              <span className={`px-2 py-0.5 rounded text-xs ${levelColors[log.level]}`}>
                {log.level}
              </span>
              <span className="text-zinc-400 w-16 flex-shrink-0">[{log.source}]</span>
              <span className="text-zinc-200">{log.message}</span>
            </div>
          ))}
          <div ref={logEndRef} />
        </div>
      </Card>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {(['INFO', 'WARNING', 'ERROR', 'DEBUG'] as LogLevel[]).map((level) => {
          const count = logs.filter((l) => l.level === level).length
          return (
            <div key={level} className="bg-zinc-900 border border-zinc-800 rounded-xl p-4">
              <div className="flex items-center justify-between">
                <p className="text-sm text-zinc-400">{level}</p>
                <span className={`px-2 py-0.5 rounded text-xs ${levelColors[level]}`}>
                  {count}
                </span>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
