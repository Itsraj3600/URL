'use client'

import Card from '@/app/(dashboard)/components/Card'

export default function HealthPage() {
  const healthChecks = [
    { name: 'MongoDB', status: 'healthy', details: '3 nodes connected', latency: '2ms' },
    { name: 'Telegram Bot', status: 'healthy', details: 'Connected to Telegram API', latency: '45ms' },
    { name: 'Index Worker', status: 'running', details: 'Processing batch #892', latency: 'N/A' },
    { name: 'Cache Service', status: 'healthy', details: 'Hit rate: 93.2%', latency: '0.1ms' },
    { name: 'Search Service', status: 'healthy', details: 'Avg response: 45ms', latency: '45ms' },
    { name: 'Web Server', status: 'healthy', details: 'Next.js running', latency: '5ms' },
  ]

  const systemMetrics = [
    { name: 'CPU Usage', value: 14, unit: '%', color: 'blue' },
    { name: 'Memory', value: 1.6, unit: 'GB', color: 'green' },
    { name: 'Disk Usage', value: 45, unit: '%', color: 'yellow' },
    { name: 'Network', value: 128, unit: 'KB/s', color: 'purple' },
  ]

  const statusColors: Record<string, string> = {
    healthy: 'bg-green-500',
    running: 'bg-blue-500',
    warning: 'bg-yellow-500',
    unhealthy: 'bg-red-500',
    idle: 'bg-zinc-500',
  }

  const statusBgColors: Record<string, string> = {
    healthy: 'bg-green-500/20 text-green-400',
    running: 'bg-blue-500/20 text-blue-400',
    warning: 'bg-yellow-500/20 text-yellow-400',
    unhealthy: 'bg-red-500/20 text-red-400',
    idle: 'bg-zinc-700/50 text-zinc-400',
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Health Monitor</h1>
          <p className="text-zinc-400">System health and metrics</p>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-3 h-3 rounded-full bg-green-500 animate-pulse" />
          <span className="text-green-400 font-medium">All Systems Operational</span>
        </div>
      </div>

      {/* System Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {systemMetrics.map((metric) => (
          <div key={metric.name} className="bg-zinc-900 border border-zinc-800 rounded-xl p-4">
            <p className="text-sm text-zinc-400">{metric.name}</p>
            <div className="flex items-end gap-1 mt-2">
              <span className="text-3xl font-bold">{metric.value}</span>
              <span className="text-zinc-500 mb-1">{metric.unit}</span>
            </div>
            <div className="mt-3 h-1 bg-zinc-800 rounded-full overflow-hidden">
              <div
                className={`h-full bg-${metric.color}-500 rounded-full`}
                style={{ width: `${Math.min(metric.value, 100)}%` }}
              />
            </div>
          </div>
        ))}
      </div>

      {/* Health Checks */}
      <Card title="Service Status" icon="💚">
        <div className="space-y-4">
          {healthChecks.map((check) => (
            <div
              key={check.name}
              className="flex items-center justify-between p-3 bg-zinc-800/50 rounded-lg"
            >
              <div className="flex items-center gap-3">
                <span className={`w-3 h-3 rounded-full ${statusColors[check.status]}`} />
                <div>
                  <p className="font-medium">{check.name}</p>
                  <p className="text-sm text-zinc-500">{check.details}</p>
                </div>
              </div>
              <div className="flex items-center gap-4">
                <span className="text-sm text-zinc-400">Latency: {check.latency}</span>
                <span className={`px-2 py-1 rounded text-sm ${statusBgColors[check.status]}`}>
                  {check.status.charAt(0).toUpperCase() + check.status.slice(1)}
                </span>
              </div>
            </div>
          ))}
        </div>
      </Card>

      {/* Database Nodes */}
      <Card title="Database Nodes" icon="🗄️">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {['Primary', 'Secondary', 'Tertiary'].map((node, i) => (
            <div
              key={node}
              className={`p-4 rounded-lg border ${
                i < 2
                  ? 'bg-green-500/10 border-green-500/30'
                  : 'bg-zinc-800/50 border-zinc-700'
              }`}
            >
              <div className="flex items-center gap-2 mb-2">
                <span className={`w-2 h-2 rounded-full ${i < 2 ? 'bg-green-500' : 'bg-zinc-500'}`} />
                <span className="font-medium">{node}</span>
              </div>
              <div className="text-sm text-zinc-400 space-y-1">
                <p>Status: {i < 2 ? 'Connected' : 'Not Configured'}</p>
                <p>Files: {i < 2 ? '245,821' : '0'}</p>
                <p>Size: {i < 2 ? '162 MB' : '0 MB'}</p>
              </div>
            </div>
          ))}
        </div>
      </Card>

      {/* Workers */}
      <Card title="Workers Status" icon="⚙️">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[1, 2, 3, 4].map((worker) => (
            <div key={worker} className="p-3 bg-zinc-800/50 rounded-lg text-center">
              <div className="w-10 h-10 rounded-full bg-blue-600 mx-auto mb-2 flex items-center justify-center">
                {worker}
              </div>
              <p className="text-sm font-medium">Worker {worker}</p>
              <p className="text-xs text-green-400">
                {worker === 1 ? 'Indexing' : worker === 2 ? 'Processing' : 'Idle'}
              </p>
            </div>
          ))}
        </div>
      </Card>

      {/* Recent Alerts */}
      <Card title="Recent Alerts" icon="🔔">
        <div className="space-y-3">
          {[
            { time: '10s ago', message: 'Cache hit rate dropped below 90%', level: 'warning' },
            { time: '5m ago', message: 'Index job started for Movies HD', level: 'info' },
            { time: '1h ago', message: 'Database connection restored', level: 'success' },
          ].map((alert, i) => (
            <div key={i} className="flex items-center gap-3 text-sm">
              <span className={`w-2 h-2 rounded-full ${
                alert.level === 'warning' ? 'bg-yellow-500' :
                alert.level === 'error' ? 'bg-red-500' :
                alert.level === 'success' ? 'bg-green-500' :
                'bg-blue-500'
              }`} />
              <span className="text-zinc-500">{alert.time}</span>
              <span className="text-zinc-300">{alert.message}</span>
            </div>
          ))}
        </div>
      </Card>
    </div>
  )
}
