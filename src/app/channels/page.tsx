'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Switch } from '@/components/ui/switch'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { formatRelativeTime } from '@/lib/utils'
import {
  Search,
  Plus,
  MoreHorizontal,
  Play,
  Pause,
  Trash2,
  Settings,
  Radio,
  RefreshCw,
  CheckCircle,
  XCircle,
} from 'lucide-react'
import { motion } from 'framer-motion'

const channels = [
  { id: -1001234567890, title: 'CINE3600 Movies', username: 'CINE3600', isActive: true, filesCount: 15023, lastIndexed: new Date(Date.now() - 5 * 60000).toISOString() },
  { id: -1002345678901, title: 'MovieWorld', username: 'MovieWorldHub', isActive: true, filesCount: 12450, lastIndexed: new Date(Date.now() - 15 * 60000).toISOString() },
  { id: -1003456789012, title: 'Series Hub', username: 'SeriesCollection', isActive: false, filesCount: 8932, lastIndexed: new Date(Date.now() - 60 * 60000).toISOString() },
  { id: -1004567890123, title: 'Kids Zone', username: 'KidsEntertainment', isActive: true, filesCount: 5621, lastIndexed: new Date(Date.now() - 30 * 60000).toISOString() },
  { id: -1005678901234, title: 'Documentaries', username: 'DocuWorld', isActive: true, filesCount: 3240, lastIndexed: new Date(Date.now() - 45 * 60000).toISOString() },
]

export default function ChannelsPage() {
  const [searchQuery, setSearchQuery] = useState('')
  const [addDialogOpen, setAddDialogOpen] = useState(false)

  return (
    <div className="space-y-6">
      {/* Page header */}
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Channels</h1>
          <p className="text-slate-400 mt-1">Manage Telegram channels connected for auto-indexing</p>
        </div>
        <Dialog open={addDialogOpen} onOpenChange={setAddDialogOpen}>
          <DialogTrigger>
            <Button className="bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700 text-white">
              <Plus className="mr-2 h-4 w-4" />
              Add Channel
            </Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-[425px] bg-slate-800 border-slate-700 text-white">
            <DialogHeader>
              <DialogTitle>Add New Channel</DialogTitle>
            </DialogHeader>
            <div className="space-y-4 pt-4">
              <Input placeholder="Channel ID (e.g. -1001234567890)" className="bg-slate-900/50 border-slate-700" />
              <Input placeholder="Channel username (e.g. @channelname)" className="bg-slate-900/50 border-slate-700" />
              <p className="text-xs text-slate-400">Make sure the bot is admin in the channel before adding.</p>
              <Button className="w-full bg-cyan-500 hover:bg-cyan-600">
                Add Channel
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {/* Stats cards */}
      <div className="grid gap-4 md:grid-cols-3">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          <Card className="border-slate-700/50 bg-slate-800/50 backdrop-blur-xl">
            <CardContent className="pt-6">
              <div className="flex items-center gap-4">
                <div className="bg-emerald-500/20 p-3 rounded-xl">
                  <CheckCircle className="h-6 w-6 text-emerald-400" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-white">4</p>
                  <p className="text-sm text-slate-400">Active Channels</p>
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
                  <XCircle className="h-6 w-6 text-amber-400" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-white">1</p>
                  <p className="text-sm text-slate-400">Inactive Channels</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
          <Card className="border-slate-700/50 bg-slate-800/50 backdrop-blur-xl">
            <CardContent className="pt-6">
              <div className="flex items-center gap-4">
                <div className="bg-cyan-500/20 p-3 rounded-xl">
                  <Radio className="h-6 w-6 text-cyan-400" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-white">45,266</p>
                  <p className="text-sm text-slate-400">Total Files</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Channels table */}
      <Card className="border-slate-700/50 bg-slate-800/50 backdrop-blur-xl">
        <CardHeader>
          <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
            <CardTitle className="text-base font-medium text-white">Connected Channels</CardTitle>
            <div className="relative w-full md:w-64">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
              <Input
                placeholder="Search channels..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-9 bg-slate-900/50 border-slate-700 text-white"
              />
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="rounded-xl border border-slate-700/50 overflow-hidden">
            <Table>
              <TableHeader>
                <TableRow className="hover:bg-slate-700/30 border-slate-700/50">
                  <TableHead className="text-slate-400">Channel</TableHead>
                  <TableHead className="text-slate-400">Files</TableHead>
                  <TableHead className="text-slate-400">Status</TableHead>
                  <TableHead className="text-slate-400">Last Indexed</TableHead>
                  <TableHead className="w-[50px]"></TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {channels.map((channel) => (
                  <TableRow key={channel.id} className="hover:bg-slate-700/30 border-slate-700/50">
                    <TableCell>
                      <div className="flex items-center gap-3">
                        <div className="bg-gradient-to-br from-cyan-500 to-blue-600 p-2 rounded-lg">
                          <Radio className="h-4 w-4 text-white" />
                        </div>
                        <div>
                          <p className="text-white font-medium">{channel.title}</p>
                          <p className="text-slate-400 text-xs">@{channel.username}</p>
                        </div>
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge className="bg-slate-700 text-slate-300">
                        {channel.filesCount.toLocaleString()} files
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        <Switch
                          checked={channel.isActive}
                          onCheckedChange={() => {}}
                        />
                        <span className={channel.isActive ? 'text-emerald-400' : 'text-slate-500'}>
                          {channel.isActive ? 'Active' : 'Paused'}
                        </span>
                      </div>
                    </TableCell>
                    <TableCell className="text-slate-400">{formatRelativeTime(channel.lastIndexed)}</TableCell>
                    <TableCell>
                      <DropdownMenu>
                        <DropdownMenuTrigger>
                          <Button variant="ghost" size="icon" className="h-8 w-8 text-slate-400 hover:text-white">
                            <MoreHorizontal className="h-4 w-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end" className="bg-slate-800 border-slate-700 text-white">
                          <DropdownMenuItem className="hover:bg-slate-700">
                            <Play className="mr-2 h-4 w-4" />
                            Start Indexing
                          </DropdownMenuItem>
                          <DropdownMenuItem className="hover:bg-slate-700">
                            <RefreshCw className="mr-2 h-4 w-4" />
                            Reindex
                          </DropdownMenuItem>
                          <DropdownMenuItem className="hover:bg-slate-700">
                            <Settings className="mr-2 h-4 w-4" />
                            Settings
                          </DropdownMenuItem>
                          <DropdownMenuItem className="text-red-400 hover:bg-red-500/10">
                            <Trash2 className="mr-2 h-4 w-4" />
                            Remove
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
