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
  DropdownMenuCheckboxItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { formatBytes, formatRelativeTime } from '@/lib/utils'
import {
  Search,
  Plus,
  MoreHorizontal,
  Trash2,
  Download,
  Filter,
  Video,
  Music,
  FileText,
  Image,
  ChevronDown,
} from 'lucide-react'
import { supabase, type Media } from '@/lib/supabase'
import { motion } from 'framer-motion'

// Mock data (in real app, this would come from Supabase)
const libraryFiles: (Media & { selected?: boolean })[] = [
  { id: '1', file_id: 'AgACsomefile1', file_name: 'Oppenheimer.2023.2160p.WEB-DL.DDP5.1.Atmos.HDR.HEVC-WEBS.mkv', file_size: 24567890123, file_type: 'video', mime_type: 'video/x-matroska', caption: null, channel_id: '@CINE3600', message_id: 1234, created_at: new Date(Date.now() - 5 * 60000).toISOString() },
  { id: '2', file_id: 'AgACsomefile2', file_name: 'Interstellar.2014.1080p.BluRay.x264.DTS-FGT.mkv', file_size: 18234567890, file_type: 'video', mime_type: 'video/x-matroska', caption: null, channel_id: '@MovieWorld', message_id: 5678, created_at: new Date(Date.now() - 10 * 60000).toISOString() },
  { id: '3', file_id: 'AgACsomefile3', file_name: 'The.Dark.Knight.2008.720p.BRRip.XviD.AC3-Rx.mp4', file_size: 2345678901, file_type: 'video', mime_type: 'video/mp4', caption: null, channel_id: '@CINE3600', message_id: 9012, created_at: new Date(Date.now() - 20 * 60000).toISOString() },
  { id: '4', file_id: 'AgACsomefile4', file_name: 'Oppenheimer.2023.Original.Soundtrack.FLAC.zip', file_size: 567890123, file_type: 'audio', mime_type: 'application/zip', caption: null, channel_id: '@CINE3600', message_id: 3456, created_at: new Date(Date.now() - 25 * 60000).toISOString() },
  { id: '5', file_id: 'AgACsomefile5', file_name: 'Dune.Part.Two.2024.Hindi.1080p.WEB-DL.msubs.DDR.mkv', file_size: 4567890123, file_type: 'video', mime_type: 'video/x-matroska', caption: null, channel_id: '@SeriesHub', message_id: 7890, created_at: new Date(Date.now() - 40 * 60000).toISOString() },
]

const getFileIcon = (type: string | null) => {
  switch (type) {
    case 'video': return Video
    case 'audio': return Music
    case 'document': return FileText
    case 'image': return Image
    default: return FileText
  }
}

const typeColors: Record<string, string> = {
  video: 'bg-cyan-500/20 text-cyan-400',
  audio: 'bg-emerald-500/20 text-emerald-400',
  document: 'bg-amber-500/20 text-amber-400',
  image: 'bg-purple-500/20 text-purple-400',
}

export default function LibraryPage() {
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedFiles, setSelectedFiles] = useState<string[]>([])

  const toggleSelectAll = () => {
    if (selectedFiles.length === libraryFiles.length) {
      setSelectedFiles([])
    } else {
      setSelectedFiles(libraryFiles.map(f => f.id))
    }
  }

  const toggleSelect = (id: string) => {
    if (selectedFiles.includes(id)) {
      setSelectedFiles(selectedFiles.filter(f => f !== id))
    } else {
      setSelectedFiles([...selectedFiles, id])
    }
  }

  return (
    <div className="space-y-6">
      {/* Page header */}
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Library</h1>
          <p className="text-slate-400 mt-1">Browse and manage your indexed files</p>
        </div>
      </div>

      {/* Library stats */}
      <div className="grid gap-4 md:grid-cols-4">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          <Card className="border-slate-700/50 bg-slate-800/50 backdrop-blur-xl">
            <CardContent className="pt-6">
              <p className="text-2xl font-bold text-white">45,231</p>
              <p className="text-sm text-slate-400">Total Files</p>
            </CardContent>
          </Card>
        </motion.div>
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
          <Card className="border-slate-700/50 bg-slate-800/50 backdrop-blur-xl">
            <CardContent className="pt-6">
              <p className="text-2xl font-bold text-white">36,542</p>
              <p className="text-sm text-slate-400">Videos</p>
            </CardContent>
          </Card>
        </motion.div>
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
          <Card className="border-slate-700/50 bg-slate-800/50 backdrop-blur-xl">
            <CardContent className="pt-6">
              <p className="text-2xl font-bold text-white">5,893</p>
              <p className="text-sm text-slate-400">Audio Files</p>
            </CardContent>
          </Card>
        </motion.div>
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
          <Card className="border-slate-700/50 bg-slate-800/50 backdrop-blur-xl">
            <CardContent className="pt-6">
              <p className="text-2xl font-bold text-white">1.2 TB</p>
              <p className="text-sm text-slate-400">Total Size</p>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Files table */}
      <Card className="border-slate-700/50 bg-slate-800/50 backdrop-blur-xl">
        <CardHeader>
          <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
            <CardTitle className="text-base font-medium text-white">
              {selectedFiles.length > 0 ? `${selectedFiles.length} files selected` : 'All Files'}
            </CardTitle>
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
              <DropdownMenu>
                <DropdownMenuTrigger>
                  <Button variant="outline" className="border-slate-700 text-slate-300 hover:bg-slate-700 hover:text-white">
                    <Filter className="mr-2 h-4 w-4" />
                    Filter
                    <ChevronDown className="ml-2 h-4 w-4" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent className="w-56 bg-slate-800 border-slate-700 text-white">
                  <DropdownMenuLabel className="text-slate-400">File Type</DropdownMenuLabel>
                  <DropdownMenuSeparator className="bg-slate-700" />
                  <DropdownMenuCheckboxItem checked>Video</DropdownMenuCheckboxItem>
                  <DropdownMenuCheckboxItem checked>Audio</DropdownMenuCheckboxItem>
                  <DropdownMenuCheckboxItem checked>Document</DropdownMenuCheckboxItem>
                  <DropdownMenuCheckboxItem checked>Image</DropdownMenuCheckboxItem>
                </DropdownMenuContent>
              </DropdownMenu>
              {selectedFiles.length > 0 && (
                <Button variant="destructive" className="bg-red-500/20 text-red-400 hover:bg-red-500/30">
                  <Trash2 className="mr-2 h-4 w-4" />
                  Delete Selected
                </Button>
              )}
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="rounded-xl border border-slate-700/50 overflow-hidden">
            <Table>
              <TableHeader>
                <TableRow className="hover:bg-slate-700/30 border-slate-700/50">
                  <TableHead className="w-[50px]">
                    <input
                      type="checkbox"
                      checked={selectedFiles.length === libraryFiles.length}
                      onChange={toggleSelectAll}
                      className="rounded border-slate-600 bg-slate-700 text-cyan-500"
                    />
                  </TableHead>
                  <TableHead className="text-slate-400">File Name</TableHead>
                  <TableHead className="text-slate-400">Type</TableHead>
                  <TableHead className="text-slate-400">Size</TableHead>
                  <TableHead className="text-slate-400">Channel</TableHead>
                  <TableHead className="text-slate-400">Added</TableHead>
                  <TableHead className="w-[50px]"></TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {libraryFiles.map((file) => {
                  const Icon = getFileIcon(file.file_type)
                  const typeColor = typeColors[file.file_type || 'document']
                  return (
                    <TableRow key={file.id} className="hover:bg-slate-700/30 border-slate-700/50">
                      <TableCell>
                        <input
                          type="checkbox"
                          checked={selectedFiles.includes(file.id)}
                          onChange={() => toggleSelect(file.id)}
                          className="rounded border-slate-600 bg-slate-700 text-cyan-500"
                        />
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-3">
                          <div className="bg-slate-700/50 p-2 rounded-lg">
                            <Icon className="h-4 w-4 text-cyan-400" />
                          </div>
                          <span className="text-white truncate max-w-[300px]">{file.file_name}</span>
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge className={typeColor}>{file.file_type || 'unknown'}</Badge>
                      </TableCell>
                      <TableCell className="text-slate-300">{formatBytes(file.file_size)}</TableCell>
                      <TableCell>
                        <Badge className="bg-slate-700 text-slate-300">{file.channel_id}</Badge>
                      </TableCell>
                      <TableCell className="text-slate-400">{formatRelativeTime(file.created_at)}</TableCell>
                      <TableCell>
                        <DropdownMenu>
                          <DropdownMenuTrigger>
                            <Button variant="ghost" size="icon" className="h-8 w-8 text-slate-400 hover:text-white">
                              <MoreHorizontal className="h-4 w-4" />
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end" className="bg-slate-800 border-slate-700 text-white">
                            <DropdownMenuItem className="hover:bg-slate-700">View details</DropdownMenuItem>
                            <DropdownMenuItem className="hover:bg-slate-700">
                              <Download className="mr-2 h-4 w-4" />
                              Download
                            </DropdownMenuItem>
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
