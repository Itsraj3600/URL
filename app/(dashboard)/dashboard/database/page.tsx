'use client'

import Card from '@/app/(dashboard)/components/Card'

const mockCollections = [
  { name: 'media', count: 492318, size: '245.8 MB', indexes: 3 },
  { name: 'users', count: 18432, size: '12.4 MB', indexes: 2 },
  { name: 'groups', count: 27, size: '0.1 MB', indexes: 2 },
  { name: 'connections', count: 15234, size: '1.2 MB', indexes: 2 },
  { name: 'index_jobs', count: 48, size: '0.05 MB', indexes: 1 },
  { name: 'statistics', count: 284521, size: '45.2 MB', indexes: 3 },
]

export default function DatabasePage() {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Database Explorer</h1>
          <p className="text-zinc-400">Browse and manage database collections</p>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-green-500" />
          <span className="text-green-400">3 nodes connected</span>
        </div>
      </div>

      {/* Database Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-4">
          <p className="text-sm text-zinc-400">Total Documents</p>
          <p className="text-2xl font-bold mt-1">839,580</p>
        </div>
        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-4">
          <p className="text-sm text-zinc-400">Total Size</p>
          <p className="text-2xl font-bold mt-1">485.2 MB</p>
        </div>
        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-4">
          <p className="text-sm text-zinc-400">Collections</p>
          <p className="text-2xl font-bold mt-1">7</p>
        </div>
        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-4">
          <p className="text-sm text-zinc-400">Indexes</p>
          <p className="text-2xl font-bold mt-1">13</p>
        </div>
      </div>

      {/* Collections */}
      <Card title="Collections" icon="🗄️">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-zinc-800 text-left">
                <th className="pb-3 text-zinc-400 font-medium">Collection</th>
                <th className="pb-3 text-zinc-400 font-medium">Documents</th>
                <th className="pb-3 text-zinc-400 font-medium">Size</th>
                <th className="pb-3 text-zinc-400 font-medium">Indexes</th>
                <th className="pb-3 text-zinc-400 font-medium">Actions</th>
              </tr>
            </thead>
            <tbody>
              {mockCollections.map((col) => (
                <tr key={col.name} className="border-b border-zinc-800/50 hover:bg-zinc-800/30">
                  <td className="py-3">
                    <span className="font-mono text-blue-400">{col.name}</span>
                  </td>
                  <td className="py-3 font-mono">{col.count.toLocaleString()}</td>
                  <td className="py-3 font-mono text-zinc-400">{col.size}</td>
                  <td className="py-3 font-mono">{col.indexes}</td>
                  <td className="py-3">
                    <div className="flex items-center gap-2">
                      <button className="px-2 py-1 bg-zinc-700 rounded text-sm hover:bg-zinc-600">
                        Browse
                      </button>
                      <button className="px-2 py-1 bg-zinc-700 rounded text-sm hover:bg-zinc-600">
                        Export
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      {/* Query Editor */}
      <Card title="Query Editor" icon="🔍">
        <div className="space-y-4">
          <div>
            <label className="block text-sm text-zinc-400 mb-1">Collection</label>
            <select className="w-full px-4 py-2 bg-zinc-800 border border-zinc-700 rounded-lg">
              {mockCollections.map((col) => (
                <option key={col.name} value={col.name}>{col.name}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm text-zinc-400 mb-1">Query (JSON)</label>
            <textarea
              className="w-full h-32 px-4 py-2 bg-zinc-800 border border-zinc-700 rounded-lg font-mono text-sm focus:outline-none focus:border-blue-500"
              placeholder='{"file_name": "avatar"}'
            />
          </div>
          <div className="flex gap-2">
            <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
              Execute Query
            </button>
            <button className="px-4 py-2 bg-zinc-700 text-zinc-300 rounded-lg hover:bg-zinc-600">
              Format JSON
            </button>
          </div>
        </div>
      </Card>
    </div>
  )
}
