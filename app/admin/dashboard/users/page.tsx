'use client';

import { useEffect, useState } from 'react';
import { fetchUsers, User } from '@/lib/dashboard-api';
import { Search, Ban, RotateCcw, Star, Trash2 } from 'lucide-react';

export default function UsersPage() {
  const [users, setUsers] = useState<User[]>([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadData = async () => {
      try {
        const data = await fetchUsers(50);
        setUsers(data);
      } catch (error) {
        console.error('[v0] Failed to load users:', error);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, []);

  const filtered = users.filter(u => u.username.toLowerCase().includes(search.toLowerCase()));

  return (
    <div className="space-y-6 p-8">
      <div>
        <h1 className="text-3xl font-bold text-white">User Manager</h1>
        <p className="text-slate-400 mt-1">Manage and monitor users</p>
      </div>

      {/* Search Bar */}
      <div className="relative">
        <Search className="absolute left-3 top-3 w-5 h-5 text-slate-400" />
        <input
          type="text"
          placeholder="Search users..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-full bg-slate-800 border border-slate-700 rounded-lg pl-10 pr-4 py-2 text-white placeholder-slate-500 focus:outline-none focus:border-blue-500"
        />
      </div>

      {/* Users Table */}
      <div className="bg-slate-800/50 border border-slate-700 rounded-lg overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-slate-600 bg-slate-900/30">
              <th className="text-left py-3 px-4 text-slate-300 font-medium">Username</th>
              <th className="text-left py-3 px-4 text-slate-300 font-medium">Searches</th>
              <th className="text-left py-3 px-4 text-slate-300 font-medium">Downloads</th>
              <th className="text-left py-3 px-4 text-slate-300 font-medium">Premium</th>
              <th className="text-left py-3 px-4 text-slate-300 font-medium">Last Seen</th>
              <th className="text-left py-3 px-4 text-slate-300 font-medium">Actions</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map(user => (
              <tr key={user.id} className="border-b border-slate-700 hover:bg-slate-700/30 transition-colors">
                <td className="py-3 px-4 text-white font-medium">{user.username}</td>
                <td className="py-3 px-4 text-slate-300">{user.searches.toLocaleString()}</td>
                <td className="py-3 px-4 text-slate-300">{user.downloads.toLocaleString()}</td>
                <td className="py-3 px-4">
                  {user.premium ? (
                    <span className="inline-flex items-center gap-1 text-yellow-400 text-xs">
                      <Star className="w-3 h-3" />
                      Premium
                    </span>
                  ) : (
                    <span className="text-slate-500 text-xs">Free</span>
                  )}
                </td>
                <td className="py-3 px-4 text-slate-400 text-xs">{user.lastSeen.toLocaleDateString()}</td>
                <td className="py-3 px-4">
                  <div className="flex gap-2">
                    <button className="p-1 hover:bg-slate-700 rounded transition-colors text-slate-400 hover:text-blue-400">
                      <RotateCcw className="w-4 h-4" title="Reset Limits" />
                    </button>
                    <button className="p-1 hover:bg-slate-700 rounded transition-colors text-slate-400 hover:text-yellow-400">
                      <Star className="w-4 h-4" title="Grant Premium" />
                    </button>
                    <button className="p-1 hover:bg-slate-700 rounded transition-colors text-slate-400 hover:text-red-400">
                      <Ban className="w-4 h-4" title="Ban" />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="text-sm text-slate-400">
        Showing {filtered.length} of {users.length} users
      </div>
    </div>
  );
}
