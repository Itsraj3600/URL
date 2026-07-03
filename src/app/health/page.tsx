'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import {
  Server,
  Database,
  Cloud,
  Wifi,
  HardDrive,
  Activity,
  CheckCircle,
  AlertTriangle,
  XCircle,
  Loader2,
  Cpu,
  Clock,
} from 'lucide-react'
import { motion } from 'framer-motion'

const services = [
  { name: 'Telegram Bot API', status: 'healthy', uptime: '99.99%', latency: '45ms', lastCheck: new Date() },
  { name: 'Supabase Database', status: 'healthy', uptime: '99.95%', latency: '12ms', lastCheck: new Date() },
  { name: 'Indexing Service', status: 'healthy', uptime: '100%', latency: 'N/A', lastCheck: new Date() },
  { name: 'File Storage', status: 'healthy', uptime: '99.8%', latency: '120ms', lastCheck: new Date() },
  { name: 'Analytics Engine', status: 'degraded', uptime: '98.5%', latency: '250ms', lastCheck: new Date() },
  { name: 'Email Service', status: 'healthy', uptime: '99.9%', latency: 'N/A', lastCheck: new Date() },
]

const metrics = [
  { label: 'CPU Usage', value: 45, max: 100, unit: '%', icon: Cpu },
  { label: 'Memory Usage', value: 62, max: 100, unit: '%', icon: HardDrive },
  { label: 'Disk Usage', value: 1.2, max: 2, unit: 'TB', icon: Database },
  { label: 'Active Connections', value: 150, max: 500, unit: '', icon: Wifi },
]

const incidents = [
  { id: 1, title: 'Analytics service degraded', status: 'investigating', date: new Date(Date.now() - 2 * 60 * 60 * 1000), message: 'Experiencing higher than normal latency on analytics endpoints' },
  { id: 2, title: 'Database maintenance completed', status: 'resolved', date: new Date(Date.now() - 24 * 60 * 60 * 1000), message: 'Scheduled maintenance completed successfully' },
]

const statusStyles = {
  healthy: { icon: CheckCircle, color: 'text-emerald-400', bg: 'bg-emerald-500/20', label: 'Healthy' },
  degraded: { icon: AlertTriangle, color: 'text-amber-400', bg: 'bg-amber-500/20', label: 'Degraded' },
  down: { icon: XCircle, color: 'text-red-400', bg: 'bg-red-500/20', label: 'Down' },
  investigating: { icon: Loader2, color: 'text-blue-400', bg: 'bg-blue-500/20', label: 'Investigating' },
  resolved: { icon: CheckCircle, color: 'text-emerald-400', bg: 'bg-emerald-500/20', label: 'Resolved' },
}

export default function HealthPage() {
  return (
    <div className="space-y-6">
      {/* Page header */}
      <div>
        <h1 className="text-2xl font-bold text-white">System Health</h1>
        <p className="text-slate-400 mt-1">Monitor system status and health</p>
      </div>

      {/* Overall status */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <Card className="border-slate-700/50 bg-gradient-to-br from-amber-500/10 to-slate-800/50 backdrop-blur-xl">
          <CardContent className="pt-6">
            <div className="flex items-center gap-4">
              <div className="bg-amber-500/20 p-4 rounded-xl">
                <AlertTriangle className="h-8 w-8 text-amber-400" />
              </div>
              <div>
                <div className="flex items-center gap-3">
                  <h2 className="text-xl font-bold text-white">Partially Degraded</h2>
                  <Badge className="bg-amber-500/20 text-amber-400">1 Service Affected</Badge>
                </div>
                <p className="text-slate-400 mt-1">Analytics service is experiencing degraded performance</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Services */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {services.map((service, index) => {
          const { icon: StatusIcon, color, bg } = statusStyles[service.status as keyof typeof statusStyles]

          return (
            <motion.div
              key={service.name}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
            >
              <Card className="border-slate-700/50 bg-slate-800/50 backdrop-blur-xl">
                <CardContent className="pt-6">
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-3">
                      <div className={bg}>
                        <Server className="h-5 w-5 text-slate-400" />
                      </div>
                      <h3 className="text-white font-medium">{service.name}</h3>
                    </div>
                    <div className={`flex items-center gap-1 ${color}`}>
                      <StatusIcon className={`h-4 w-4 ${service.status === 'investigating' ? 'animate-spin' : ''}`} />
                      <span className="text-sm">{statusStyles[service.status as keyof typeof statusStyles].label}</span>
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-slate-500 text-xs">Uptime</p>
                      <p className="text-white text-sm font-medium">{service.uptime}</p>
                    </div>
                    <div>
                      <p className="text-slate-500 text-xs">Latency</p>
                      <p className="text-white text-sm font-medium">{service.latency}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          )
        })}
      </div>

      {/* System metrics */}
      <Card className="border-slate-700/50 bg-slate-800/50 backdrop-blur-xl">
        <CardHeader>
          <CardTitle className="text-base font-medium text-white">System Metrics</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-6 md:grid-cols-4">
            {metrics.map((metric) => {
              const Icon = metric.icon
              const percentage = (metric.value / metric.max) * 100

              return (
                <div key={metric.label} className="space-y-2">
                  <div className="flex items-center gap-2">
                    <Icon className="h-4 w-4 text-cyan-400" />
                    <span className="text-slate-400 text-sm">{metric.label}</span>
                  </div>
                  <div className="flex items-end justify-between">
                    <span className="text-2xl font-bold text-white">
                      {metric.value}{metric.unit}
                    </span>
                    <span className="text-slate-500 text-sm">/ {metric.max}{metric.unit}</span>
                  </div>
                  <div className="h-2 bg-slate-700 rounded-full overflow-hidden">
                    <div
                      className={`h-full transition-all ${
                        percentage > 80 ? 'bg-red-500' : percentage > 60 ? 'bg-amber-500' : 'bg-cyan-500'
                      }`}
                      style={{ width: `${Math.min(percentage, 100)}%` }}
                    />
                  </div>
                </div>
              )
            })}
          </div>
        </CardContent>
      </Card>

      {/* Recent incidents */}
      <Card className="border-slate-700/50 bg-slate-800/50 backdrop-blur-xl">
        <CardHeader>
          <CardTitle className="text-base font-medium text-white">Recent Incidents</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {incidents.map((incident) => {
              const { icon: StatusIcon, color, bg } = statusStyles[incident.status as keyof typeof statusStyles]

              return (
                <div key={incident.id} className="bg-slate-700/30 rounded-xl p-4">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <StatusIcon className={`h-4 w-4 ${color} ${incident.status === 'investigating' ? 'animate-spin' : ''}`} />
                      <span className="text-white font-medium">{incident.title}</span>
                    </div>
                    <Badge className={bg}>{statusStyles[incident.status as keyof typeof statusStyles].label}</Badge>
                  </div>
                  <p className="text-slate-400 text-sm">{incident.message}</p>
                  <div className="flex items-center gap-2 mt-2 text-xs text-slate-500">
                    <Clock className="h-3 w-3" />
                    {incident.date.toLocaleString()}
                  </div>
                </div>
              )
            })}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
