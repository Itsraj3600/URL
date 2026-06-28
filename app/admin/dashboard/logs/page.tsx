'use client';

import { useState } from 'react';
import { Search, Download } from 'lucide-react';

const mockLogs = [
  { id: 1, level: 'INFO', message: 'User session started', timestamp: new Date(Date.now() - 5000) },
  { id: 2, level: 'WARNING', message: 'High memory usage detected', timestamp: new Date(Date.now() - 15000) },
  { id: 3, level: 'ERROR', message: 'Database connection timeout', timestamp: new Date(Date.now() - 45000) },
  { id: 4, level: 'INFO', message: 'Search index updated', timestamp: new Date(Date.now() - 120000) },
  { id: 5, level: 'WARNING', message: 'Telegram rate limit approaching', timestamp: new Date(Date.now() - 300000) },
  { id: 6, level: 'INFO', message: 'Worker 1 restarted', timestamp: new Date(Date.now() - 600000) },
];

export default function LogsPage() {
  const [filter, setFilter] = useState<'ALL' | 'INFO' | 'WARNING' | 'ERROR'>('ALL');
  const [search, setSearch] = useState('');

  const filtered = mockLogs.filter(log => {
    if (filter !== 'ALL' && log.level !== filter) return false;
    if (search && !log.message.toLowerCase().includes(search.toLowerCase())) return false;
    return true;
  });

  return (
    <div className="space-y-6 p-8">
      <div>
        <h1 className="text-3xl font-bold text-white">Live Logs</h1>
        <p className="text-slate-400 mt-1">Real-time system logs and events</p>
      </div>

      {/* Controls */}
      <div className="flex flex-col md:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-3 w-5 h-5 text-slate-400" />
          <input
            type="text"
            placeholder="Search logs..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full bg-slate-800 border border-slate-700 rounded-lg pl-10 pr-4 py-2 text-white placeholder-slate-500 focus:outline-none focus:border-blue-500"
          />
        </div>
        <div className="flex gap-2">
          {(['ALL', 'INFO', 'WARNING', 'ERROR'] as const).map(level => (
            <button
              key={level}
              onClick={() => setFilter(level)}
              className={`px-4 py-2 rounded transition-colors ${
                filter === level
                  ? 'bg-blue-600 text-white'
                  : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
              }`}
            >
              {level}
            </button>
          ))}
        </div>
        <button className="flex items-center gap-2 px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded transition-colors">
          <Download className="w-4 h-4" />
          Export
        </button>
      </div>

      {/* Logs List */}
      <div className="bg-slate-800/50 border border-slate-700 rounded-lg overflow-hidden">
        <div className="max-h-96 overflow-y-auto">
          {filtered.map(log => (
            <div
              key={log.id}
              className={`px-4 py-3 border-b border-slate-700 hover:bg-slate-700/30 transition-colors font-mono text-sm ${
                log.level === 'ERROR' ? 'bg-red-900/10' :
                log.level === 'WARNING' ? 'bg-amber-900/10' :
                'bg-slate-800/50'
              }`}
            >
              <div className="flex items-center gap-3">
                <span className={`text-xs font-bold px-2 py-1 rounded ${
                  log.level === 'ERROR' ? 'bg-red-900 text-red-200' :
                  log.level === 'WARNING' ? 'bg-amber-900 text-amber-200' :
                  'bg-blue-900 text-blue-200'
                }`}>
                  {log.level}
                </span>
                <span className="text-slate-400 text-xs">
                  {log.timestamp.toLocaleTimeString()}
                </span>
                <span className="text-slate-300">{log.message}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="text-sm text-slate-400">
        Showing {filtered.length} of {mockLogs.length} logs
      </div>
    </div>
  );
}
