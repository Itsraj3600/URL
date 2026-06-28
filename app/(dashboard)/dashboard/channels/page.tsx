'use client'

import Card from '@/app/(dashboard)/components/Card'

const mockChannels = [
  { id: 1, name: 'Movies HD', username: 'movies_hd_official', files: 481942, last_sync: '4 sec ago', status: 'active' },
  { id: 2, name: 'TV Shows Central', username: 'tvshows_central', files: 128432, last_sync: '1 min ago', status: 'active' },
  { id: 3, name: 'Anime Collection', username: 'anime_collect', files: 62118, last_sync: '5 min ago', status: 'syncing' },
  { id: 4, name: 'Documentaries', username: 'docs_channel', files: 34821, last_sync: '1 hour ago', status: 'paused' },
]

export default function ChannelsPage() {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Channel Manager</h1>
          <p className="text-zinc-400">Manage indexed channels</p>
        </div>
        <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
          + Add Channel
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-4">
          <p className="text-sm text-zinc-400">Total Channels</p>
          <p className="text-2xl font-bold mt-1">27</p>
        </div>
        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-4">
          <p className="text-sm text-zinc-400">Active</p>
          <p className="text-2xl font-bold mt-1 text-green-400">23</p>
        </div>
        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-4">
          <p className="text-sm text-zinc-400">Syncing</p>
          <p className="text-2xl font-bold mt-1 text-blue-400">3</p>
        </div>
        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-4">
          <p className="text-sm text-zinc-400">Paused</p>
          <p className="text-2xl font-bold mt-1 text-yellow-400">1</p>
        </div>
      </div>

      {/* Channels List */}
      <Card title="Channels" icon="📡">
        <div className="space-y-4">
          {mockChannels.map((channel) => (
            <div
              key={channel.id}
              className="flex items-center justify-between p-4 bg-zinc-800/50 rounded-lg hover:bg-zinc-800 transition-colors"
            >
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-full bg-blue-600 flex items-center justify-center text-lg font-bold">
                  {channel.name.charAt(0)}
                </div>
                <div>
                  <p className="font-semibold">{channel.name}</p>
                  <p className="text-sm text-zinc-500">@{channel.username}</p>
                </div>
              </div>

              <div className="flex items-center gap-8 text-sm text-zinc-400">
                <div className="text-center">
                  <p className="text-lg font-mono text-zinc-200">{channel.files.toLocaleString()}</p>
                  <p className="text-xs">Files</p>
                </div>
                <div className="text-center">
                  <p className="text-zinc-300">{channel.last_sync}</p>
                  <p className="text-xs">Last Sync</p>
                </div>
                <div className="flex items-center gap-2">
                  <span className={`w-2 h-2 rounded-full ${
                    channel.status === 'active' ? 'bg-green-500' :
                    channel.status === 'syncing' ? 'bg-blue-500 animate-pulse' :
                    'bg-yellow-500'
                  }`} />
                  <span className={`${
                    channel.status === 'active' ? 'text-green-400' :
                    channel.status === 'syncing' ? 'text-blue-400' :
                    'text-yellow-400'
                  }`}>
                    {channel.status.charAt(0).toUpperCase() + channel.status.slice(1)}
                  </span>
                </div>
              </div>

              <div className="flex items-center gap-2">
                <button className="px-3 py-1 bg-zinc-700 text-zinc-300 rounded text-sm hover:bg-zinc-600">
                  Sync
                </button>
                <button className="px-3 py-1 bg-zinc-700 text-zinc-300 rounded text-sm hover:bg-zinc-600">
                  {channel.status === 'paused' ? 'Resume' : 'Pause'}
                </button>
                <button className="p-1 text-zinc-400 hover:text-zinc-200">
                  ⋯
                </button>
              </div>
            </div>
          ))}
        </div>
      </Card>

      {/* Add Channel */}
      <Card title="Add New Channel" icon="➕">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm text-zinc-400 mb-1">Channel Username or ID</label>
            <input
              type="text"
              placeholder="@channel_name or -1001234567890"
              className="w-full px-4 py-2 bg-zinc-800 border border-zinc-700 rounded-lg text-sm focus:outline-none focus:border-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm text-zinc-400 mb-1">Last Message ID (optional)</label>
            <input
              type="number"
              placeholder="Leave empty for all"
              className="w-full px-4 py-2 bg-zinc-800 border border-zinc-700 rounded-lg text-sm focus:outline-none focus:border-blue-500"
            />
          </div>
          <div className="flex items-end">
            <button className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
              Add Channel
            </button>
          </div>
        </div>
      </Card>
    </div>
  )
}
