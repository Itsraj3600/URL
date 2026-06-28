'use client'

import { useState } from 'react'
import Card from '@/app/(dashboard)/components/Card'

const mockUsers = [
  { id: 1, user_id: 123456789, username: 'john_doe', first_name: 'John', searches: 7218, downloads: 19842, premium: true, banned: false, last_seen: '2 min ago' },
  { id: 2, user_id: 987654321, username: 'jane_smith', first_name: 'Jane', searches: 1523, downloads: 8923, premium: false, banned: false, last_seen: '1 hour ago' },
  { id: 3, user_id: 456789123, username: 'movie_fan', first_name: 'Bob', searches: 8942, downloads: 34521, premium: true, banned: false, last_seen: '5 min ago' },
  { id: 4, user_id: 789123456, username: 'bad_user', first_name: 'Spam', searches: 0, downloads: 0, premium: false, banned: true, last_seen: 'Never' },
]

export default function UsersPage() {
  const [search, setSearch] = useState('')
  const [filter, setFilter] = useState<'all' | 'premium' | 'banned'>('all')

  const filteredUsers = mockUsers.filter(user => {
    if (filter === 'premium' && !user.premium) return false
    if (filter === 'banned' && !user.banned) return false
    if (search && !user.username.toLowerCase().includes(search.toLowerCase()) && !user.first_name.toLowerCase().includes(search.toLowerCase())) return false
    return true
  })

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">User Management</h1>
          <p className="text-zinc-400">Manage and monitor users</p>
        </div>
        <div className="text-sm text-zinc-400">
          Total: {mockUsers.length.toLocaleString()} users
        </div>
      </div>

      {/* Filters */}
      <Card>
        <div className="flex flex-wrap items-center gap-4">
          {/* Search */}
          <div className="flex-1 min-w-[200px]">
            <input
              type="text"
              placeholder="Search by username or name..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full px-4 py-2 bg-zinc-800 border border-zinc-700 rounded-lg text-sm focus:outline-none focus:border-blue-500"
            />
          </div>

          {/* Filter buttons */}
          <div className="flex items-center gap-2">
            {['all', 'premium', 'banned'].map((f) => (
              <button
                key={f}
                onClick={() => setFilter(f as any)}
                className={`px-3 py-1 rounded-lg text-sm transition-colors ${
                  filter === f
                    ? 'bg-blue-600 text-white'
                    : 'bg-zinc-800 text-zinc-400 hover:bg-zinc-700'
                }`}
              >
                {f.charAt(0).toUpperCase() + f.slice(1)}
              </button>
            ))}
          </div>
        </div>
      </Card>

      {/* Users Table */}
      <Card>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-zinc-800 text-left">
                <th className="pb-3 text-zinc-400 font-medium">User</th>
                <th className="pb-3 text-zinc-400 font-medium">ID</th>
                <th className="pb-3 text-zinc-400 font-medium">Searches</th>
                <th className="pb-3 text-zinc-400 font-medium">Downloads</th>
                <th className="pb-3 text-zinc-400 font-medium">Status</th>
                <th className="pb-3 text-zinc-400 font-medium">Last Seen</th>
                <th className="pb-3 text-zinc-400 font-medium">Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredUsers.map((user) => (
                <tr key={user.id} className="border-b border-zinc-800/50 hover:bg-zinc-800/30">
                  <td className="py-3">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center text-sm">
                        {user.first_name?.charAt(0) || '?'}
                      </div>
                      <div>
                        <p className="font-medium">{user.first_name}</p>
                        <p className="text-sm text-zinc-500">@{user.username}</p>
                      </div>
                    </div>
                  </td>
                  <td className="py-3 font-mono text-sm text-zinc-400">
                    {user.user_id}
                  </td>
                  <td className="py-3 font-mono">
                    {user.searches.toLocaleString()}
                  </td>
                  <td className="py-3 font-mono">
                    {user.downloads.toLocaleString()}
                  </td>
                  <td className="py-3">
                    <div className="flex items-center gap-2">
                      {user.premium && (
                        <span className="px-2 py-0.5 text-xs bg-purple-500/20 text-purple-400 rounded">
                          Premium
                        </span>
                      )}
                      {user.banned && (
                        <span className="px-2 py-0.5 text-xs bg-red-500/20 text-red-400 rounded">
                          Banned
                        </span>
                      )}
                      {!user.premium && !user.banned && (
                        <span className="px-2 py-0.5 text-xs bg-zinc-700 text-zinc-400 rounded">
                          Free
                        </span>
                      )}
                    </div>
                  </td>
                  <td className="py-3 text-sm text-zinc-400">
                    {user.last_seen}
                  </td>
                  <td className="py-3">
                    <div className="flex items-center gap-2">
                      <button className="p-1 rounded hover:bg-zinc-700 text-zinc-400 hover:text-zinc-200">
                        👁️
                      </button>
                      <button className="p-1 rounded hover:bg-zinc-700 text-zinc-400 hover:text-zinc-200">
                        {user.banned ? '🔓' : '🚫'}
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  )
}
