'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
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
import { formatBytes, formatRelativeTime } from '@/lib/utils'
import {
  Search,
  Plus,
  MoreHorizontal,
  Play,
  Pause,
  RefreshCw,
  Trash2,
  Filter,
  Download,
  Film,
  Music,
  FileText,
  Image,
  Video,
} from 'lucide-react'
import { motion } from 'framer-motion'

// Mock data for indexing status
const indexingChannels = [
  { id: 1, name: '@CINE3600', status: 'active', files: 15023, lastIndexed: new Date(Date.now() - 5 * 60000).toISOString(), progress: 100 },
  { id: 2, name: '@MovieWorld', status: 'active', files: 12450, lastIndexed: new Date(Date.now() - 15 * 60000).toISOString(), progress: 78 },
  { id: 3, name: '@SeriesHub', status: 'paused', files: 8932, lastIndexed: new Date(Date.now() - 60 * 60000).toISOString(), progress: 45 },
  { id: 4, name: '@KidsZone', status: 'active', files: 5621, lastIndexed: new Date(Date.now() - 30 * 60000).toISOString(), progress: 100 },
]

const recentFiles = [
  { id: '1', name: 'Oppenheimer.2023.2160p.WEB-DL.DDP5.1.Atmos.HDR.HEVC-WEBS.mkv', size: 24567890123, type: 'video', channel: '@CINE3600', date: new Date(Date.now() - 5 * 60000).toISOString() },
  { id: '2', name: 'Interstellar.2014.1080p.BluRay.x264.DTS-FGT.mkv', size: 18234567890, type: 'video', channel: '@MovieWorld', date: new Date(Date.now() - 10 * 60000).toISOString() },
  { id: '3', name: 'The.Dark.Knight.2008.720p.BRRip.XviD.AC3-Rx.mp4', size: 2345678901, type: 'video', channel: '@CINE3600', date: new Date(Date.now() - 20 * 60000).toISOString() },
  { id: '4', name: 'Oppenheimer.2023.Original.Soundtrack.FLAC.zip', size: 567890123, type: 'audio', channel: '@CINE3600', date: new Date(Date.now() - 25 * 60000).toISOString() },
  { id: '5', name: 'Dune.Part.Two.2024.Hindi.1080p.WEB-DL.msubs.DDR.mkv', size: 4567890123, type: 'video', channel: '@SeriesHub', date: new Date(Date.now() - 40 * 60000).toISOString() },
  { id: '6', name: 'The.Office.US.S01E01.720p.WEB-DL.en.srt', size: 45678, type: 'document', channel: '@SeriesHub', date: new Date(Date.now() - 45 * 60000).toISOString() },
]

const getFileIcon = (type: string) => {
  switch (type) {
    case 'video': return Video
    case 'audio': return Music
    case 'document': return FileText
    case 'image': return Image
    default: return Film
  }
}

export default function IndexingPage() {
  const [searchQuery, setSearchQuery] = useState('')

  return (
    <div className="space-y-6">
      {/* Page header */}
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Indexing</h1>
          <p className="text-slate-400 mt-1">Manage your file indexing from Telegram channels</p>
        </div>
        <div className="flex gap-3">
          <Button className="bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700 text-white">
            <Plus className="mr-2 h-4 w-4" />
            Add Channel
          </Button>
        </div>
      </div>

      {/* Indexing status cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {indexingChannels.map((channel, index) => (
          <motion.div
            key={channel.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: index * 0.1 }}
          >
            <Card className="border-slate-700/50 bg-slate-800/50 backdrop-blur-xl">
              <CardHeader className="pb-2">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-sm font-medium text-white">{channel.name}</CardTitle>
                  <Badge
                    variant={channel.status === 'active' ? 'default' : 'secondary'}
                    className={channel.status === 'active' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-amber-500/20 text-amber-400'}
                  >
                    {channel.status}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-slate-400">Files indexed</span>
                  <span className="text-white font-medium">{channel.files.toLocaleString()}</span>
                </div>
                {channel.progress < 100 && (
                  <div className="w-full bg-slate-700 rounded-full h-1.5">
                    <div
                      className="bg-cyan-500 h-1.5 rounded-full transition-all"
                      style={{ width: `${channel.progress}%` }}
                    />
                  </div>
                )}
                <div className="flex items-center justify-between text-xs text-slate-500">
                  <span>Last: {formatRelativeTime(channel.lastIndexed)}</span>
                  <div className="flex gap-1">
                    <Button variant="ghost" size="icon" className="h-7 w-7 text-slate-400 hover:text-white">
                      {channel.status === 'active' ? <Pause className="h-3 w-3" /> : <Play className="h-3 w-3" />}
                    </Button>
                    <Button variant="ghost" size="icon" className="h-7 w-7 text-slate-400 hover:text-white">
                      <RefreshCw className="h-3 w-3" />
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </div>

      {/* Recent files section */}
      <Card className="border-slate-700/50 bg-slate-800/50 backdrop-blur-xl">
        <CardHeader>
          <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
            <CardTitle className="text-base font-medium text-white">Recently Indexed Files</CardTitle>
            <div className="flex gap-2">
              <div className="relative flex-1 md:w-64">
                <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
                <Input
                  placeholder="Search files..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-9 bg-slate-900/50 border-slate-700 text-white"
                />
              </div>
              <Button variant="outline" className="border-slate-700 text-slate-300 hover:bg-slate-700 hover:text-white">
                <Filter className="mr-2 h-4 w-4" />
                Filter
              </Button>
              <Button variant="outline" className="border-slate-700 text-slate-300 hover:bg-slate-700 hover:text-white">
                <Download className="mr-2 h-4 w-4" />
                Export
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="rounded-xl border border-slate-700/50 overflow-hidden">
            <Table>
              <TableHeader>
                <TableRow className="hover:bg-slate-700/30 border-slate-700/50">
                  <TableHead className="text-slate-400">File Name</TableHead>
                  <TableHead className="text-slate-400">Size</TableHead>
                  <TableHead className="text-slate-400">Channel</TableHead>
                  <TableHead className="text-slate-400">Indexed</TableHead>
                  <TableHead className="w-[50px]"></TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {recentFiles.map((file) => {
                  const Icon = getFileIcon(file.type)
                  return (
                    <TableRow key={file.id} className="hover:bg-slate-700/30 border-slate-700/50">
                      <TableCell>
                        <div className="flex items-center gap-3">
                          <div className="bg-slate-700/50 p-2 rounded-lg">
                            <Icon className="h-4 w-4 text-cyan-400" />
                          </div>
                          <span className="text-white truncate max-w-[300px]">{file.name}</span>
                        </div>
                      </TableCell>
                      <TableCell className="text-slate-300">{formatBytes(file.size)}</TableCell>
                      <TableCell>
                        <Badge className="bg-slate-700 text-slate-300">{file.channel}</Badge>
                      </TableCell>
                      <TableCell className="text-slate-400">{formatRelativeTime(file.date)}</TableCell>
                      <TableCell>
                        <DropdownMenu>
                          <DropdownMenuTrigger>
                            <Button variant="ghost" size="icon" className="h-8 w-8 text-slate-400 hover:text-white">
                              <MoreHorizontal className="h-4 w-4" />
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end" className="bg-slate-800 border-slate-700 text-white">
                            <DropdownMenuItem className="hover:bg-slate-700">View details</DropdownMenuItem>
                            <DropdownMenuItem className="hover:bg-slate-700">Download</DropdownMenuItem>
                            <DropdownMenuItem className="text-red-400 hover:bg-red-500/10">
                              <Trash2 className="mr-2 h-4 w-4" />
                              Delete
                            </DropdownMenuItem>
                          </DropdownMenuContent>
                        </DropdownMenu>
                      </TableCell>
                    </TableRow>
                  )
                })}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
