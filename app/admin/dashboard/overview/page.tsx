'use client';

import { useEffect, useState } from 'react';
import { Activity, Users, Film, Tv, Sparkles, Radio, TrendingUp, Download, Users2, Activity as ActivityIcon } from 'lucide-react';
import { StatCard } from '@/components/dashboard/stat-card';
import { fetchBotStats, fetchWorkers, fetchSystemHealth, fetchAlerts, BotStats, WorkerStatus, SystemHealth, SystemAlert } from '@/lib/dashboard-api';
import { LineChart, Line, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

export default function OverviewPage() {
  const [botStats, setBotStats] = useState<BotStats | null>(null);
  const [workers, setWorkers] = useState<WorkerStatus[]>([]);
  const [health, setHealth] = useState<SystemHealth | null>(null);
  const [alerts, setAlerts] = useState<SystemAlert[]>([]);
  const [searchData, setSearchData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadData = async () => {
      try {
        const [botData, workersData, healthData, alertsData] = await Promise.all([
          fetchBotStats(),
          fetchWorkers(),
          fetchSystemHealth(),
          fetchAlerts(3),
        ]);

        setBotStats(botData);
        setWorkers(workersData);
        setHealth(healthData);
        setAlerts(alertsData);

        // Generate fake search trend data
        const trend = Array.from({ length: 12 }, (_, i) => ({
          time: `${i}:00`,
          searches: Math.floor(Math.random() * 500) + 200,
        }));
        setSearchData(trend);
      } catch (error) {
        console.error('[v0] Failed to load overview data:', error);
      } finally {
        setLoading(false);
      }
    };

    loadData();
    const interval = setInterval(loadData, 5000);
    return () => clearInterval(interval);
  }, []);

  if (loading || !botStats || !health) {
    return <div className="p-8 text-slate-400">Loading...</div>;
  }

  const statusColor = botStats.status === 'online' ? 'online' : botStats.status === 'busy' ? 'warning' : 'offline';

  return (
    <div className="space-y-8 p-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Dashboard</h1>
          <p className="text-slate-400 mt-1">Real-time bot monitoring and analytics</p>
        </div>
        <div className="flex items-center gap-2">
          <div className={`w-3 h-3 rounded-full ${statusColor === 'online' ? 'bg-emerald-500' : statusColor === 'warning' ? 'bg-amber-500' : 'bg-red-500'}`} />
          <span className="text-sm font-medium text-slate-300 capitalize">{botStats.status}</span>
        </div>
      </div>

      {/* Quick Stats Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-4">
        <StatCard label="Bot Status" value={botStats.status.toUpperCase()} icon={Activity} status={statusColor as any} />
        <StatCard label="Users" value={botStats.users.toLocaleString()} icon={Users} trend={Math.floor(Math.random() * 20) - 10} />
        <StatCard label="Movies" value={botStats.movies.toLocaleString()} icon={Film} />
        <StatCard label="TV Shows" value={botStats.tvShows.toLocaleString()} icon={Tv} />
        <StatCard label="Anime" value={botStats.anime.toLocaleString()} icon={Sparkles} />
        <StatCard label="Channels" value={botStats.channels} icon={Radio} />
        <StatCard label="Today's Searches" value={botStats.todaySearches.toLocaleString()} icon={TrendingUp} />
        <StatCard label="Downloads" value={botStats.downloads.toLocaleString()} icon={Download} />
        <StatCard label="Cache Hit" value={`${botStats.cacheHitRate.toFixed(1)}%`} icon={ActivityIcon} />
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Search Trend Chart */}
        <div className="lg:col-span-2 bg-slate-800/50 border border-slate-700 rounded-lg p-6">
          <h2 className="text-lg font-semibold text-white mb-4">Search Activity (Last 12 Hours)</h2>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={searchData}>
              <defs>
                <linearGradient id="colorSearches" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.8} />
                  <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#475569" />
              <XAxis dataKey="time" stroke="#94a3b8" />
              <YAxis stroke="#94a3b8" />
              <Tooltip 
                contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #475569' }}
                labelStyle={{ color: '#e2e8f0' }}
              />
              <Area type="monotone" dataKey="searches" stroke="#3b82f6" fillOpacity={1} fill="url(#colorSearches)" />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* System Health */}
        <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-6">
          <h2 className="text-lg font-semibold text-white mb-4">System Health</h2>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm text-slate-400">MongoDB</span>
              <span className={`text-xs px-2 py-1 rounded ${health.mongodb === 'healthy' ? 'bg-emerald-900 text-emerald-200' : health.mongodb === 'degraded' ? 'bg-amber-900 text-amber-200' : 'bg-red-900 text-red-200'}`}>
                {health.mongodb}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-slate-400">Telegram</span>
              <span className={`text-xs px-2 py-1 rounded ${health.telegram === 'healthy' ? 'bg-emerald-900 text-emerald-200' : health.telegram === 'degraded' ? 'bg-amber-900 text-amber-200' : 'bg-red-900 text-red-200'}`}>
                {health.telegram}
              </span>
            </div>
            <div className="pt-4 border-t border-slate-600 space-y-2">
              <p className="text-sm text-slate-300">Uptime: {(health.uptime / 3600).toFixed(1)}h</p>
              <p className="text-sm text-slate-300">CPU: {health.cpuUsage.toFixed(1)}%</p>
              <p className="text-sm text-slate-300">RAM: {health.ramUsage.toFixed(1)}%</p>
            </div>
          </div>
        </div>
      </div>

      {/* Workers Summary */}
      <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-6">
        <h2 className="text-lg font-semibold text-white mb-4">Active Workers</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {workers.map(worker => (
            <div key={worker.id} className="bg-slate-700/50 border border-slate-600 rounded-lg p-4">
              <div className="flex items-center justify-between mb-3">
                <h3 className="font-medium text-white capitalize">{worker.id}</h3>
                <div className={`w-2 h-2 rounded-full ${worker.status === 'busy' ? 'bg-yellow-500' : worker.status === 'idle' ? 'bg-emerald-500' : 'bg-slate-500'}`} />
              </div>
              <div className="text-sm space-y-1 text-slate-300">
                <p>CPU: {worker.cpu.toFixed(1)}%</p>
                <p>RAM: {worker.ram}MB</p>
                <p>Queue: {worker.queue} items</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Recent Alerts */}
      {alerts.length > 0 && (
        <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-6">
          <h2 className="text-lg font-semibold text-white mb-4">Recent Alerts</h2>
          <div className="space-y-2">
            {alerts.map(alert => (
              <div key={alert.id} className={`px-4 py-2 rounded text-sm flex items-center justify-between ${
                alert.severity === 'critical' ? 'bg-red-900/20 text-red-200 border border-red-900' :
                alert.severity === 'warning' ? 'bg-amber-900/20 text-amber-200 border border-amber-900' :
                'bg-blue-900/20 text-blue-200 border border-blue-900'
              }`}>
                <span>{alert.message}</span>
                <span className="text-xs text-slate-400">{Math.floor((Date.now() - alert.timestamp.getTime()) / 60000)}m ago</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
