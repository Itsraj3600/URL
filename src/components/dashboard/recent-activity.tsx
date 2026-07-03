'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { cn, formatRelativeTime } from '@/lib/utils'
import { Activity, FileText, User, Radio, TrendingUp } from 'lucide-react'
import { motion } from 'framer-motion'

type ActivityItem = {
  id: string
  type: 'file' | 'user' | 'channel' | 'search'
  title: string
  description: string
  timestamp: string
}

const activities: ActivityItem[] = [
  {
    id: '1',
    type: 'file',
    title: 'New file indexed',
    description: 'Oppenheimer.2023.2160p.WEB-DL.mkv',
    timestamp: new Date(Date.now() - 2 * 60000).toISOString(),
  },
  {
    id: '2',
    type: 'user',
    title: 'New user registered',
    description: 'User @movie_fan joined the bot',
    timestamp: new Date(Date.now() - 5 * 60000).toISOString(),
  },
  {
    id: '3',
    type: 'channel',
    title: 'Channel connected',
    description: '@MovieWorld added for indexing',
    timestamp: new Date(Date.now() - 15 * 60000).toISOString(),
  },
  {
    id: '4',
    type: 'search',
    title: 'Popular search',
    description: '"Interstellar" searched 156 times today',
    timestamp: new Date(Date.now() - 30 * 60000).toISOString(),
  },
  {
    id: '5',
    type: 'file',
    title: 'Files deleted',
    description: '5 CamRip files were removed',
    timestamp: new Date(Date.now() - 45 * 60000).toISOString(),
  },
]

const iconMap = {
  file: FileText,
  user: User,
  channel: Radio,
  search: TrendingUp,
}

const colorMap = {
  file: 'bg-cyan-500/20 text-cyan-400',
  user: 'bg-emerald-500/20 text-emerald-400',
  channel: 'bg-blue-500/20 text-blue-400',
  search: 'bg-amber-500/20 text-amber-400',
}

export function RecentActivity() {
  return (
    <Card className="border-slate-700/50 bg-slate-800/50 backdrop-blur-xl">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="text-base font-medium text-white">Recent Activity</CardTitle>
          <Badge className="bg-slate-700 text-slate-300 hover:bg-slate-600">
            Live
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {activities.map((activity, index) => {
          const Icon = iconMap[activity.type]
          const colorClass = colorMap[activity.type]

          return (
            <motion.div
              key={activity.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.3, delay: index * 0.1 }}
              className="flex items-start gap-3"
            >
              <div className={cn('rounded-lg p-2', colorClass.split(' ')[0])}>
                <Icon className={cn('h-4 w-4', colorClass.split(' ')[1])} />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-white truncate">{activity.title}</p>
                <p className="text-xs text-slate-400 truncate">{activity.description}</p>
              </div>
              <span className="text-xs text-slate-500 whitespace-nowrap">
                {formatRelativeTime(activity.timestamp)}
              </span>
            </motion.div>
          )
        })}
      </CardContent>
    </Card>
  )
}
