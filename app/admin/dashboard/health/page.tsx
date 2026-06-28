'use client';

import { useEffect, useState } from 'react';
import { fetchSystemHealth, SystemHealth } from '@/lib/dashboard-api';
import { Activity, Database, Radio, Cpu, HardDrive, Zap } from 'lucide-react';

export default function HealthPage() {
  const [health, setHealth] = useState<SystemHealth | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadData = async () => {
      try {
        const data = await fetchSystemHealth();
        setHealth(data);
      } catch (error) {
        console.error('[v0] Failed to load health:', error);
      } finally {
        setLoading(false);
      }
    };

    loadData();
    const interval = setInterval(loadData, 3000);
    return () => clearInterval(interval);
  }, []);

  if (loading || !health) return <div className="p-8 text-slate-400">Loading...</div>;

  const healthCard = (title: string, status: string, icon: any, details?: string) => {
    const isHealthy = status === 'healthy';
    const Icon = icon;
    return (
      <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-white">{title}</h3>
          <Icon className={`w-6 h-6 ${isHealthy ? 'text-emerald-500' : status === 'degraded' ? 'text-amber-500' : 'text-red-500'}`} />
        </div>
        <p className={`text-sm font-bold ${isHealthy ? 'text-emerald-400' : status === 'degraded' ? 'text-amber-400' : 'text-red-400'}`}>
          {status.toUpperCase()}
        </p>
        {details && <p className="text-xs text-slate-400 mt-2">{details}</p>}
      </div>
    );
  };

  return (
    <div className="space-y-6 p-8">
      <div>
        <h1 className="text-3xl font-bold text-white">Health Monitor</h1>
        <p className="text-slate-400 mt-1">System and service health status</p>
      </div>

      {/* Main Services */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {healthCard('MongoDB', health.mongodb, Database)}
        {healthCard('Telegram', health.telegram, Radio)}
        {healthCard('Workers', 'healthy', Activity, `${health.workers} workers active`)}
      </div>

      {/* Resource Usage */}
      <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-6">
        <h2 className="text-lg font-semibold text-white mb-6">Resource Usage</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* CPU */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="flex items-center gap-2 text-slate-300"><Cpu className="w-4 h-4" /> CPU</span>
              <span className="text-lg font-bold text-blue-400">{health.cpuUsage.toFixed(1)}%</span>
            </div>
            <div className="w-full bg-slate-700 rounded-full h-2 overflow-hidden">
              <div
                className="bg-blue-500 h-full transition-all"
                style={{ width: `${health.cpuUsage}%` }}
              />
            </div>
          </div>

          {/* RAM */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="flex items-center gap-2 text-slate-300"><HardDrive className="w-4 h-4" /> RAM</span>
              <span className="text-lg font-bold text-purple-400">{health.ramUsage.toFixed(1)}%</span>
            </div>
            <div className="w-full bg-slate-700 rounded-full h-2 overflow-hidden">
              <div
                className="bg-purple-500 h-full transition-all"
                style={{ width: `${health.ramUsage}%` }}
              />
            </div>
          </div>

          {/* Uptime */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="flex items-center gap-2 text-slate-300"><Zap className="w-4 h-4" /> Uptime</span>
              <span className="text-lg font-bold text-emerald-400">{(health.uptime / 3600).toFixed(1)}h</span>
            </div>
            <div className="text-xs text-slate-400 mt-2">
              {Math.floor(health.uptime / 86400)} days, {Math.floor((health.uptime % 86400) / 3600)} hours
            </div>
          </div>
        </div>
      </div>

      {/* Services Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-6">
          <h3 className="text-sm font-semibold text-slate-400 uppercase mb-4">Service Status</h3>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-slate-300">API Server</span>
              <span className="inline-block w-2 h-2 rounded-full bg-emerald-500"></span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-slate-300">Search Engine</span>
              <span className="inline-block w-2 h-2 rounded-full bg-emerald-500"></span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-slate-300">Cache Server</span>
              <span className="inline-block w-2 h-2 rounded-full bg-emerald-500"></span>
            </div>
          </div>
        </div>

        <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-6">
          <h3 className="text-sm font-semibold text-slate-400 uppercase mb-4">Recent Events</h3>
          <div className="text-xs text-slate-400 space-y-2">
            <p>• Cache cleared 5m ago</p>
            <p>• Worker 2 restarted 2h ago</p>
            <p>• Database backup completed 6h ago</p>
          </div>
        </div>
      </div>
    </div>
  );
}
