'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
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
import { formatBytes } from '@/lib/utils'
import {
  Database,
  RefreshCw,
  DatabaseBackup,
  HardDrive,
  Table2,
  BarChart,
  Clock,
  AlertTriangle,
} from 'lucide-react'
import { motion } from 'framer-motion'

const tableStats = [
  { name: 'media', rowCount: 45231, totalRows: '45,231', sizeMB: 1256.78, sizeHuman: '1.23 GB', lastUpdated: new Date(Date.now() - 5 * 60000).toISOString() },
  { name: 'users', rowCount: 8549, totalRows: '8,549', sizeMB: 12.34, sizeHuman: '12 MB', lastUpdated: new Date(Date.now() - 15 * 60000).toISOString() },
  { name: 'groups', rowCount: 124, totalRows: '124', sizeMB: 2.45, sizeHuman: '2.4 MB', lastUpdated: new Date(Date.now() - 30 * 60000).toISOString() },
  { name: 'channels', rowCount: 24, totalRows: '24', sizeMB: 0.87, sizeHuman: '870 KB', lastUpdated: new Date(Date.now() - 60 * 60000).toISOString() },
  { name: 'filters', rowCount: 456, totalRows: '456', sizeMB: 1.23, sizeHuman: '1.2 MB', lastUpdated: new Date(Date.now() - 45 * 60000).toISOString() },
  { name: 'logs', rowCount: 125000, totalRows: '125,000', sizeMB: 234.56, sizeHuman: '235 MB', lastUpdated: new Date(Date.now() - 1 * 60000).toISOString() },
  { name: 'stats', rowCount: 365, totalRows: '365', sizeMB: 0.45, sizeHuman: '450 KB', lastUpdated: new Date(Date.now() - 120 * 60000).toISOString() },
]

export default function DatabasePage() {
  const [isLoading, setIsLoading] = useState(false)

  return (
    <div className="space-y-6">
      {/* Page header */}
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Database</h1>
          <p className="text-slate-400 mt-1">Monitor and manage your Supabase database</p>
        </div>
        <div className="flex gap-3">
          <Button variant="outline" className="border-slate-700 text-slate-300 hover:bg-slate-700 hover:text-white">
            <RefreshCw className="mr-2 h-4 w-4" />
            Refresh
          </Button>
          <Button className="bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700 text-white">
            <DatabaseBackup className="mr-2 h-4 w-4" />
            Backup Database
          </Button>
        </div>
      </div>

      {/* Database status */}
      <div className="grid gap-4 md:grid-cols-4">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          <Card className="border-slate-700/50 bg-slate-800/50 backdrop-blur-xl">
            <CardContent className="pt-6">
              <div className="flex items-center gap-4">
                <div className="bg-cyan-500/20 p-3 rounded-xl">
                  <HardDrive className="h-6 w-6 text-cyan-400" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-white">1.5 GB</p>
                  <p className="text-sm text-slate-400">Total Size</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
          <Card className="border-slate-700/50 bg-slate-800/50 backdrop-blur-xl">
            <CardContent className="pt-6">
              <div className="flex items-center gap-4">
                <div className="bg-emerald-500/20 p-3 rounded-xl">
                  <Table2 className="h-6 w-6 text-emerald-400" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-white">7</p>
                  <p className="text-sm text-slate-400">Tables</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
          <Card className="border-slate-700/50 bg-slate-800/50 backdrop-blur-xl">
            <CardContent className="pt-6">
              <div className="flex items-center gap-4">
                <div className="bg-purple-500/20 p-3 rounded-xl">
                  <BarChart className="h-6 w-6 text-purple-400" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-white">180K</p>
                  <p className="text-sm text-slate-400">Total Rows</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
          <Card className="border-slate-700/50 bg-slate-800/50 backdrop-blur-xl">
            <CardContent className="pt-6">
              <div className="flex items-center gap-4">
                <div className="bg-amber-500/20 p-3 rounded-xl">
                  <Clock className="h-6 w-6 text-amber-400" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-white">45ms</p>
                  <p className="text-sm text-slate-400">Avg Query Time</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Connection info */}
      <Card className="border-slate-700/50 bg-slate-800/50 backdrop-blur-xl">
        <CardHeader>
          <CardTitle className="text-base font-medium text-white">Connection Status</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-3">
            <div className="bg-slate-700/30 rounded-xl p-4">
              <div className="flex items-center gap-2 mb-2">
                <div className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
                <span className="text-emerald-400 font-medium">Connected</span>
              </div>
              <p className="text-slate-400 text-sm">Supabase PostgreSQL</p>
            </div>
            <div className="bg-slate-700/30 rounded-xl p-4">
              <p className="text-slate-400 text-sm mb-1">Host</p>
              <p className="text-white text-sm font-mono truncate">sliycmaxapvrlooihxgp.supabase.co</p>
            </div>
            <div className="bg-slate-700/30 rounded-xl p-4">
              <p className="text-slate-400 text-sm mb-1">Connection Pool</p>
              <p className="text-white font-mono">15 / 50 active</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Tables list */}
      <Card className="border-slate-700/50 bg-slate-800/50 backdrop-blur-xl">
        <CardHeader>
          <CardTitle className="text-base font-medium text-white">Database Tables</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="rounded-xl border border-slate-700/50 overflow-hidden">
            <Table>
              <TableHeader>
                <TableRow className="hover:bg-slate-700/30 border-slate-700/50">
                  <TableHead className="text-slate-400">Table Name</TableHead>
                  <TableHead className="text-slate-400">Rows</TableHead>
                  <TableHead className="text-slate-400">Size</TableHead>
                  <TableHead className="text-slate-400">Status</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {tableStats.map((table) => (
                  <TableRow key={table.name} className="hover:bg-slate-700/30 border-slate-700/50">
                    <TableCell>
                      <div className="flex items-center gap-3">
                        <div className="bg-cyan-500/20 p-2 rounded-lg">
                          <Table2 className="h-4 w-4 text-cyan-400" />
                        </div>
                        <code className="text-white">{table.name}</code>
                      </div>
                    </TableCell>
                    <TableCell className="text-slate-300">{table.totalRows}</TableCell>
                    <TableCell className="text-slate-300">{table.sizeHuman}</TableCell>
                    <TableCell>
                      <Badge className="bg-emerald-500/20 text-emerald-400">Healthy</Badge>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>

      {/* Maintenance info */}
      <Card className="border-slate-700/50 bg-slate-800/50 backdrop-blur-xl">
        <CardHeader>
          <CardTitle className="text-base font-medium text-white">Maintenance</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-2">
            <div className="bg-slate-700/30 rounded-xl p-4">
              <div className="flex items-center gap-2 mb-2">
                <Clock className="h-4 w-4 text-slate-400" />
                <span className="text-white font-medium">Last Backup</span>
              </div>
              <p className="text-slate-400 text-sm">2026-07-03 at 00:00 UTC</p>
            </div>
            <div className="bg-slate-700/30 rounded-xl p-4">
              <div className="flex items-center gap-2 mb-2">
                <DatabaseBackup className="h-4 w-4 text-slate-400" />
                <span className="text-white font-medium">Auto Backups</span>
              </div>
              <p className="text-emerald-400 text-sm">Enabled - Daily at 00:00 UTC</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
