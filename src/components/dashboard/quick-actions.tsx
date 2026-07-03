'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import {
  RefreshCw,
  Play,
  Pause,
  Database,
  Trash2,
  Settings,
  Shield
} from 'lucide-react'

export function QuickActions() {
  return (
    <Card className="border-slate-700/50 bg-slate-800/50 backdrop-blur-xl">
      <CardHeader>
        <CardTitle className="text-base font-medium text-white">Quick Actions</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        <Button
          variant="outline"
          className="w-full justify-start gap-3 bg-slate-700/30 border-slate-600 hover:bg-slate-700 hover:text-white"
        >
          <RefreshCw className="h-4 w-4 text-cyan-400" />
          Reindex All Channels
          <Badge className="ml-auto bg-cyan-500/20 text-cyan-400">Auto</Badge>
        </Button>

        <Button
          variant="outline"
          className="w-full justify-start gap-3 bg-slate-700/30 border-slate-600 hover:bg-slate-700 hover:text-white"
        >
          <Play className="h-4 w-4 text-emerald-400" />
          Start Indexing
        </Button>

        <Button
          variant="outline"
          className="w-full justify-start gap-3 bg-slate-700/30 border-slate-600 hover:bg-slate-700 hover:text-white"
        >
          <Pause className="h-4 w-4 text-amber-400" />
          Pause Bot
        </Button>

        <Button
          variant="outline"
          className="w-full justify-start gap-3 bg-slate-700/30 border-slate-600 hover:bg-slate-700 hover:text-white"
        >
          <Database className="h-4 w-4 text-blue-400" />
          Backup Database
        </Button>

        <Button
          variant="outline"
          className="w-full justify-start gap-3 bg-slate-700/30 border-slate-600 hover:bg-slate-700 hover:text-white"
        >
          <Trash2 className="h-4 w-4 text-red-400" />
          Clean Bad Files
          <Badge className="ml-auto bg-red-500/20 text-red-400">CamRip & PreDVD</Badge>
        </Button>

        <Button
          variant="outline"
          className="w-full justify-start gap-3 bg-slate-700/30 border-slate-600 hover:bg-red-500/20 hover:text-red-400"
        >
          <Shield className="h-4 w-4" />
          Security Settings
        </Button>
      </CardContent>
    </Card>
  )
}
