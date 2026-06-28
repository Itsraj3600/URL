'use client';

import { Users2, TrendingUp } from 'lucide-react';

const mockChannels = [
  { id: 1, name: 'Movies HD', subscribers: 125000, posts: 1240, growth: '+12%' },
  { id: 2, name: 'TV Shows 4K', subscribers: 98000, posts: 856, growth: '+8%' },
  { id: 3, name: 'Anime Hub', subscribers: 67000, posts: 523, growth: '+15%' },
  { id: 4, name: 'New Releases', subscribers: 145000, posts: 2104, growth: '+5%' },
];

export default function ChannelsPage() {
  return (
    <div className="space-y-6 p-8">
      <div>
        <h1 className="text-3xl font-bold text-white">Channels</h1>
        <p className="text-slate-400 mt-1">Manage Telegram channels</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {mockChannels.map(channel => (
          <div key={channel.id} className="bg-slate-800/50 border border-slate-700 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-white mb-4">{channel.name}</h3>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-slate-400 flex items-center gap-2"><Users2 className="w-4 h-4" /> Subscribers</span>
                <span className="text-white font-bold">{(channel.subscribers / 1000).toFixed(0)}K</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-slate-400">Posts</span>
                <span className="text-white font-bold">{channel.posts.toLocaleString()}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-slate-400 flex items-center gap-2"><TrendingUp className="w-4 h-4" /> Growth</span>
                <span className="text-green-400 font-bold">{channel.growth}</span>
              </div>
              <button className="w-full mt-4 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded transition-colors">
                View Channel
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
