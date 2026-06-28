'use client'

import Card from '@/app/(dashboard)/components/Card'

export default function AnalyticsPage() {
  const popularQueries = [
    { query: 'Interstellar', count: 8942, change: '+12%' },
    { query: 'Avatar', count: 7821, change: '+8%' },
    { query: 'The Matrix', count: 6543, change: '+5%' },
    { query: 'Inception', count: 5892, change: '+3%' },
    { query: 'Avengers', count: 4521, change: '-2%' },
    { query: 'Spider-Man', count: 4128, change: '+1%' },
  ]

  const hourlyData = [
    { hour: '00:00', searches: 1200 },
    { hour: '04:00', searches: 450 },
    { hour: '08:00', searches: 890 },
    { hour: '12:00', searches: 2100 },
    { hour: '16:00', searches: 2800 },
    { hour: '20:00', searches: 3500 },
    { hour: '23:00', searches: 2200 },
  ]

  const maxSearches = Math.max(...hourlyData.map(d => d.searches))

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Search Analytics</h1>
          <p className="text-zinc-400">Search patterns and popular queries</p>
        </div>
        <div className="flex items-center gap-2">
          <select className="px-3 py-1 bg-zinc-800 border border-zinc-700 rounded-lg text-sm">
            <option>Last 24 Hours</option>
            <option>Last 7 Days</option>
            <option>Last 30 Days</option>
          </select>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-4">
          <p className="text-sm text-zinc-400">Total Searches</p>
          <p className="text-2xl font-bold mt-1">52,117</p>
          <p className="text-xs text-green-400 mt-1">+12% from yesterday</p>
        </div>
        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-4">
          <p className="text-sm text-zinc-400">Unique Queries</p>
          <p className="text-2xl font-bold mt-1">8,432</p>
          <p className="text-xs text-zinc-400 mt-1">Distinct search terms</p>
        </div>
        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-4">
          <p className="text-sm text-zinc-400">Avg Results</p>
          <p className="text-2xl font-bold mt-1">12.4</p>
          <p className="text-xs text-zinc-400 mt-1">Per search</p>
        </div>
        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-4">
          <p className="text-sm text-zinc-400">No Results Rate</p>
          <p className="text-2xl font-bold mt-1">3.2%</p>
          <p className="text-xs text-red-400 mt-1">+0.5% from avg</p>
        </div>
      </div>

      {/* Searches by Hour */}
      <Card title="Searches by Hour" icon="📊">
        <div className="flex items-end gap-1 h-48">
          {hourlyData.map((data, i) => (
            <div key={i} className="flex-1 flex flex-col items-center">
              <div
                className="w-full bg-blue-600 rounded-t hover:bg-blue-500 transition-colors cursor-pointer"
                style={{ height: `${(data.searches / maxSearches) * 100}%` }}
                title={`${data.searches} searches`}
              />
              <span className="text-xs text-zinc-500 mt-2">{data.hour}</span>
            </div>
          ))}
        </div>
      </Card>

      {/* Popular Queries */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <Card title="Popular Queries" icon="🔥">
          <div className="space-y-3">
            {popularQueries.map((item, i) => (
              <div key={i} className="flex items-center justify-between p-2 hover:bg-zinc-800/50 rounded-lg">
                <div className="flex items-center gap-3">
                  <span className="w-6 h-6 rounded bg-zinc-700 flex items-center justify-center text-sm font-bold">
                    {i + 1}
                  </span>
                  <span className="font-medium">{item.query}</span>
                </div>
                <div className="flex items-center gap-4">
                  <span className="text-zinc-400">{item.count.toLocaleString()}</span>
                  <span className={`text-sm ${
                    item.change.startsWith('+') ? 'text-green-400' : 'text-red-400'
                  }`}>
                    {item.change}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </Card>

        <Card title="Performance Metrics" icon="⚡">
          <div className="space-y-4">
            <div className="p-3 bg-zinc-800/50 rounded-lg">
              <div className="flex justify-between mb-2">
                <span className="text-zinc-400">Cache Hit Rate</span>
                <span className="font-mono">93.2%</span>
              </div>
              <div className="h-2 bg-zinc-700 rounded-full overflow-hidden">
                <div className="h-full bg-green-500 rounded-full" style={{ width: '93.2%' }} />
              </div>
            </div>
            <div className="p-3 bg-zinc-800/50 rounded-lg">
              <div className="flex justify-between mb-2">
                <span className="text-zinc-400">Avg Search Time</span>
                <span className="font-mono">45ms</span>
              </div>
              <div className="h-2 bg-zinc-700 rounded-full overflow-hidden">
                <div className="h-full bg-blue-500 rounded-full" style={{ width: '45%' }} />
              </div>
            </div>
            <div className="p-3 bg-zinc-800/50 rounded-lg">
              <div className="flex justify-between mb-2">
                <span className="text-zinc-400">MongoDB Latency</span>
                <span className="font-mono">12ms</span>
              </div>
              <div className="h-2 bg-zinc-700 rounded-full overflow-hidden">
                <div className="h-full bg-purple-500 rounded-full" style={{ width: '12%' }} />
              </div>
            </div>
          </div>
        </Card>
      </div>

      {/* Failed Searches */}
      <Card title="Failed Searches (No Results)" icon="❌">
        <div className="space-y-3">
          {[
            { query: 'Avengers Endgame 4K HDR', count: 156 },
            { query: 'Oppenheimer IMAX', count: 124 },
            { query: 'Game of Thrones S08', count: 98 },
          ].map((item, i) => (
            <div key={i} className="flex items-center justify-between p-2 bg-red-500/10 border border-red-500/20 rounded-lg">
              <span className="text-red-400">{item.query}</span>
              <div className="flex items-center gap-2">
                <span className="text-zinc-400 text-sm">{item.count} searches</span>
                <button className="px-2 py-1 text-xs bg-zinc-700 rounded hover:bg-zinc-600">
                  Add to Index
                </button>
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  )
}
