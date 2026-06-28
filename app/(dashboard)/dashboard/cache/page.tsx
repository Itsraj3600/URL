'use client'

import Card from '@/app/(dashboard)/components/Card'

export default function CachePage() {
  const cacheStats = [
    { name: 'Search Cache', entries: 8432, hitRate: 93.2, size: '12.4 MB', ttl: '10 min' },
    { name: 'Pagination Cache', entries: 2451, hitRate: 88.5, size: '2.1 MB', ttl: '15 min' },
    { name: 'Metadata Cache', entries: 15234, hitRate: 95.1, size: '45.2 MB', ttl: '60 min' },
    { name: 'Session Cache', entries: 892, hitRate: 76.3, size: '0.5 MB', ttl: '30 min' },
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Cache Manager</h1>
          <p className="text-zinc-400">Monitor and manage caches</p>
        </div>
        <button className="px-4 py-2 bg-red-600/20 text-red-400 rounded-lg hover:bg-red-600/30 transition-colors">
          Clear All Caches
        </button>
      </div>

      {/* Overview */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-4">
          <p className="text-sm text-zinc-400">Total Entries</p>
          <p className="text-2xl font-bold mt-1">27,009</p>
        </div>
        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-4">
          <p className="text-sm text-zinc-400">Overall Hit Rate</p>
          <p className="text-2xl font-bold mt-1 text-green-400">93.2%</p>
        </div>
        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-4">
          <p className="text-sm text-zinc-400">Total Size</p>
          <p className="text-2xl font-bold mt-1">60.2 MB</p>
        </div>
        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-4">
          <p className="text-sm text-zinc-400">Memory Usage</p>
          <p className="text-2xl font-bold mt-1 text-zinc-300">1.6 GB</p>
        </div>
      </div>

      {/* Cache Details */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {cacheStats.map((cache) => (
          <Card key={cache.name} title={cache.name} icon="⚡">
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-zinc-400">Hit Rate</span>
                <span className="font-mono text-green-400">{cache.hitRate}%</span>
              </div>
              <div className="h-2 bg-zinc-700 rounded-full overflow-hidden">
                <div
                  className={`h-full rounded-full ${
                    cache.hitRate > 90 ? 'bg-green-500' :
                    cache.hitRate > 70 ? 'bg-yellow-500' :
                    'bg-red-500'
                  }`}
                  style={{ width: `${cache.hitRate}%` }}
                />
              </div>
              <div className="grid grid-cols-3 gap-4 text-sm">
                <div>
                  <p className="text-zinc-500">Entries</p>
                  <p className="font-mono">{cache.entries.toLocaleString()}</p>
                </div>
                <div>
                  <p className="text-zinc-500">Size</p>
                  <p className="font-mono">{cache.size}</p>
                </div>
                <div>
                  <p className="text-zinc-500">TTL</p>
                  <p className="font-mono">{cache.ttl}</p>
                </div>
              </div>
              <div className="flex gap-2 pt-2 border-t border-zinc-800">
                <button className="px-3 py-1 bg-zinc-700 text-zinc-300 rounded text-sm hover:bg-zinc-600">
                  Clear
                </button>
                <button className="px-3 py-1 bg-zinc-700 text-zinc-300 rounded text-sm hover:bg-zinc-600">
                  Warm
                </button>
                <button className="px-3 py-1 bg-zinc-700 text-zinc-300 rounded text-sm hover:bg-zinc-600">
                  Stats
                </button>
              </div>
            </div>
          </Card>
        ))}
      </div>

      {/* Cache Operations */}
      <Card title="Cache Operations" icon="⚙️">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button className="p-4 bg-zinc-800/50 border border-zinc-700 rounded-lg hover:bg-zinc-800 transition-colors text-left">
            <p className="font-semibold mb-1">Warm Cache</p>
            <p className="text-sm text-zinc-500">Pre-populate cache with popular queries</p>
          </button>
          <button className="p-4 bg-zinc-800/50 border border-zinc-700 rounded-lg hover:bg-zinc-800 transition-colors text-left">
            <p className="font-semibold mb-1">Optimize</p>
            <p className="text-sm text-zinc-500">Remove expired and least-used entries</p>
          </button>
          <button className="p-4 bg-zinc-800/50 border border-zinc-700 rounded-lg hover:bg-zinc-800 transition-colors text-left">
            <p className="font-semibold mb-1">Export Stats</p>
            <p className="text-sm text-zinc-500">Download cache statistics as JSON</p>
          </button>
        </div>
      </Card>
    </div>
  )
}
