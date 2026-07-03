'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { formatRelativeTime } from '@/lib/utils'
import { Search, Filter, Download, Trash2, FileText, AlertTriangle, AlertCircle, Info, Bot } from 'lucide-react'
import { motion } from 'framer-motion'

type LogLevel = 'info' | 'warning' | 'error'

const logs: { id: string; level: LogLevel; source: string; message: string; timestamp: string; data: Record<string, unknown> }[] = [
  { id: '1', level: 'info', source: 'bot', message: 'User @moviefan sent a search request for "Oppenheimer"', timestamp: new Date(Date.now() - 1 * 60000).toISOString(), data: { userId: 123456789 } },
  { id: '2', level: 'info', source: 'indexing', message: 'Successfully indexed 23 new files from @CINE3600', timestamp: new Date(Date.now() - 5 * 60000).toISOString(), data: { channelId: -1001234567890, filesCount: 23 } },
  { id: '3', level: 'warning', source: 'api', message: 'Rate limit approached for user 987654321 (450/500 requests)', timestamp: new Date(Date.now() - 10 * 60000).toISOString(), data: { userId: 987654321, requests: 450 } },
  { id: '4', level: 'error', source: 'bot', message: 'Failed to send file to user 456789123 - File not found', timestamp: new Date(Date.now() - 15 * 60000).toISOString(), data: { userId: 456789123, fileId: 'AgACmissingfile' } },
  { id: '5', level: 'info', source: 'webhook', message: 'Broadcast sent to 124 premium users', timestamp: new Date(Date.now() - 20 * 60000).toISOString(), data: { recipients: 124 } },
  { id: '6', level: 'info', source: 'premium', message: 'Premium access granted to user @moviefan (Silver Plan - 30 days)', timestamp: new Date(Date.now() - 25 * 60000).toISOString(), data: { userId: 123456789, plan: 'silver' } },
  { id: '7', level: 'warning', source: 'database', message: 'Slow query detected (2.3s) - media search for "movie_name"', timestamp: new Date(Date.now() - 30 * 60000).toISOString(), data: { queryTime: 2.3 } },
  { id: '8', level: 'error', source: 'api', message: 'Telegram API error 429 - Too Many Requests, retry after 30s', timestamp: new Date(Date.now() - 35 * 60000).toISOString(), data: { retryAfter: 30 } },
  { id: '9', level: 'info', source: 'bot', message: 'New user registered: @cinemalover (ID: 321654987)', timestamp: new Date(Date.now() - 40 * 60000).toISOString(), data: { userId: 321654987 } },
  { id: '10', level: 'info', source: 'indexing', message: 'Indexing completed for @MovieWorld - 156 total files', timestamp: new Date(Date.now() - 60 * 60000).toISOString(), data: { channelId: -1002345678901, filesCount: 156 } },
]

const levelStyles: Record<LogLevel, { icon: typeof Info; color: string; badge: string }> = {
  info: { icon: Info, color: 'bg-cyan-500/20 text-cyan-400', badge: 'bg-cyan-500/20 text-cyan-400' },
  warning: { icon: AlertTriangle, color: 'bg-amber-500/20 text-amber-400', badge: 'bg-amber-500/20 text-amber-400' },
  error: { icon: AlertCircle, color: 'bg-red-500/20 text-red-400', badge: 'bg-red-500/20 text-red-400' },
}

const sourceStyles: Record<string, string> = {
  bot: 'bg-blue-500/20 text-blue-400',
  indexing: 'bg-purple-500/20 text-purple-400',
  api: 'bg-emerald-500/20 text-emerald-400',
  database: 'bg-rose-500/20 text-rose-400',
  premium: 'bg-amber-500/20 text-amber-400',
  webhook: 'bg-slate-500/20 text-slate-400',
}

export default function LogsPage() {
  const [searchQuery, setSearchQuery] = useState('')
  const [levelFilter, setLevelFilter] = useState<string | null>(null)

  return (
    <div className="space-y-6">
      {/* Page header */}
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Logs</h1>
          <p className="text-slate-400 mt-1">View and manage system logs</p>
        </div>
        <div className="flex gap-3">
          <Button variant="outline" className="border-slate-700 text-slate-300 hover:bg-slate-700 hover:text-white">
            <Download className="mr-2 h-4 w-4" />
            Export Logs
          </Button>
          <Button variant="outline" className="border-red-700/50 text-red-400 hover:bg-red-500/10">
            <Trash2 className="mr-2 h-4 w-4" />
            Clear Logs
          </Button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid gap-4 md:grid-cols-4">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          <Card className="border-slate-700/50 bg-slate-800/50 backdrop-blur-xl">
            <CardContent className="pt-6">
              <div className="flex items-center gap-4">
                <div className="bg-cyan-500/20 p-3 rounded-xl">
                  <Info className="h-6 w-6 text-cyan-400" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-white">125,430</p>
                  <p className="text-sm text-slate-400">Total Logs</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
          <Card className="border-slate-700/50 bg-slate-800/50 backdrop-blur-xl">
            <CardContent className="pt-6">
              <div className="flex items-center gap-4">
                <div className="bg-amber-500/20 p-3 rounded-xl">
                  <AlertTriangle className="h-6 w-6 text-amber-400" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-white">234</p>
                  <p className="text-sm text-slate-400">Warnings</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
          <Card className="border-slate-700/50 bg-slate-800/50 backdrop-blur-xl">
            <CardContent className="pt-6">
              <div className="flex items-center gap-4">
                <div className="bg-red-500/20 p-3 rounded-xl">
                  <AlertCircle className="h-6 w-6 text-red-400" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-white">45</p>
                  <p className="text-sm text-slate-400">Errors</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
          <Card className="border-slate-700/50 bg-slate-800/50 backdrop-blur-xl">
            <CardContent className="pt-6">
              <div className="flex items-center gap-4">
                <div className="bg-purple-500/20 p-3 rounded-xl">
                  <Bot className="h-6 w-6 text-purple-400" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-white">12</p>
                  <p className="text-sm text-slate-400">Today</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Filters */}
      <div className="flex gap-4">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
          <Input
            placeholder="Search logs..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-9 bg-slate-900/50 border-slate-700 text-white"
          />
        </div>
        <DropdownMenu>
          <DropdownMenuTrigger>
            <Button variant="outline" className="border-slate-700 text-slate-300 hover:bg-slate-700 hover:text-white">
              <Filter className="mr-2 h-4 w-4" />
              {levelFilter ? `Level: ${levelFilter}` : 'All Levels'}
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent className="bg-slate-800 border-slate-700 text-white">
            <DropdownMenuLabel className="text-slate-400">Filter by Level</DropdownMenuLabel>
            <DropdownMenuSeparator className="bg-slate-700" />
            <DropdownMenuItem onClick={() => setLevelFilter(null)}>All Levels</DropdownMenuItem>
            <DropdownMenuItem onClick={() => setLevelFilter('info')}>Info</DropdownMenuItem>
            <DropdownMenuItem onClick={() => setLevelFilter('warning')}>Warning</DropdownMenuItem>
            <DropdownMenuItem onClick={() => setLevelFilter('error')}>Error</DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>

      {/* Logs list */}
      <Card className="border-slate-700/50 bg-slate-800/50 backdrop-blur-xl">
        <CardContent className="pt-6">
          <div className="space-y-2">
            {logs.map((log, index) => {
              const { icon: LevelIcon, badge: levelBadge } = levelStyles[log.level]
              const sourceStyle = sourceStyles[log.source] || 'bg-slate-500/20 text-slate-400'

              return (
                <motion.div
                  key={log.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.3, delay: index * 0.05 }}
                  className="group relative bg-slate-700/20 hover:bg-slate-700/30 rounded-xl p-4 border border-slate-700/50 transition-colors"
                >
                  <div className="flex items-start gap-4">
                    <div className={`p-2 rounded-lg ${levelBadge.split(' ')[0]}`}>
                      <LevelIcon className="h-4 w-4" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <Badge className={levelBadge}>{log.level}</Badge>
                        <Badge className={sourceStyle}>{log.source}</Badge>
                        <span className="text-slate-500 text-xs">{formatRelativeTime(log.timestamp)}</span>
                      </div>
                      <p className="text-white">{log.message}</p>
                      {log.data && Object.keys(log.data).length > 0 && (
                        <pre className="mt-2 text-xs text-slate-400 bg-slate-900/50 p-2 rounded-lg overflow-x-auto">
                          {JSON.stringify(log.data, null, 2)}
                        </pre>
                      )}
                    </div>
                    <FileText className="h-4 w-4 text-slate-600 opacity-0 group-hover:opacity-100 transition-opacity" />
                  </div>
                </motion.div>
              )
            })}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
