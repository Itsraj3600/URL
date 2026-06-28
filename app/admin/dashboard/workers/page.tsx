'use client';

import { useEffect, useState } from 'react';
import { fetchWorkers, WorkerStatus } from '@/lib/dashboard-api';
import { Play, Pause, RotateCcw, Zap, HardDrive } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

export default function WorkersPage() {
  const [workers, setWorkers] = useState<WorkerStatus[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedWorker, setSelectedWorker] = useState<string | null>(null);
  const [cpuHistory, setCpuHistory] = useState<any[]>([]);

  useEffect(() => {
    const loadData = async () => {
      try {
        const data = await fetchWorkers();
        setWorkers(data);
        if (!selectedWorker && data.length > 0) {
          setSelectedWorker(data[0].id);
        }

        // Generate CPU history
        const history = Array.from({ length: 20 }, (_, i) => ({
          time: i,
          cpu: Math.random() * 100,
        }));
        setCpuHistory(history);
      } catch (error) {
        console.error('[v0] Failed to load workers:', error);
      } finally {
        setLoading(false);
      }
    };

    loadData();
    const interval = setInterval(loadData, 3000);
    return () => clearInterval(interval);
  }, []);

  const selected = workers.find(w => w.id === selectedWorker);

  return (
    <div className="space-y-6 p-8">
      <div>
        <h1 className="text-3xl font-bold text-white">Worker Monitor</h1>
        <p className="text-slate-400 mt-1">Manage and monitor bot workers</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Workers List */}
        <div className="lg:col-span-1 space-y-3">
          <h2 className="text-lg font-semibold text-white">Workers</h2>
          {workers.map(worker => (
            <button
              key={worker.id}
              onClick={() => setSelectedWorker(worker.id)}
              className={`w-full text-left p-4 rounded-lg border transition-colors ${
                selectedWorker === worker.id
                  ? 'bg-blue-900/30 border-blue-600'
                  : 'bg-slate-800/50 border-slate-700 hover:border-slate-600'
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <h3 className="font-medium text-white capitalize">{worker.id}</h3>
                <div className={`w-2 h-2 rounded-full ${
                  worker.status === 'busy' ? 'bg-yellow-500' :
                  worker.status === 'idle' ? 'bg-emerald-500' :
                  'bg-slate-400'
                }`} />
              </div>
              <p className="text-xs text-slate-400">CPU: {worker.cpu.toFixed(1)}% | RAM: {worker.ram}MB</p>
            </button>
          ))}
        </div>

        {/* Selected Worker Details */}
        {selected && (
          <div className="lg:col-span-2 space-y-4">
            {/* Status Card */}
            <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-6">
              <h2 className="text-lg font-semibold text-white mb-4 capitalize">{selected.id} Details</h2>
              <div className="grid grid-cols-2 gap-4 mb-6">
                <div>
                  <p className="text-sm text-slate-400 mb-1">Status</p>
                  <p className={`text-xl font-bold capitalize ${
                    selected.status === 'busy' ? 'text-yellow-400' :
                    selected.status === 'idle' ? 'text-emerald-400' :
                    'text-slate-400'
                  }`}>{selected.status}</p>
                </div>
                <div>
                  <p className="text-sm text-slate-400 mb-1">Queue</p>
                  <p className="text-xl font-bold text-white">{selected.queue} items</p>
                </div>
                <div>
                  <p className="text-sm text-slate-400 mb-1">CPU Usage</p>
                  <p className="text-xl font-bold text-blue-400">{selected.cpu.toFixed(1)}%</p>
                </div>
                <div>
                  <p className="text-sm text-slate-400 mb-1">RAM Usage</p>
                  <p className="text-xl font-bold text-purple-400">{selected.ram}MB</p>
                </div>
              </div>

              {selected.currentJob && (
                <div className="bg-slate-700/50 rounded-lg p-4 mb-6">
                  <p className="text-sm text-slate-400 mb-1">Current Job</p>
                  <p className="text-white font-medium">{selected.currentJob}</p>
                </div>
              )}

              {/* Control Buttons */}
              <div className="flex gap-3">
                <button className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors">
                  <Play className="w-4 h-4" />
                  Resume
                </button>
                <button className="flex items-center gap-2 px-4 py-2 bg-amber-600 hover:bg-amber-700 text-white rounded-lg transition-colors">
                  <Pause className="w-4 h-4" />
                  Pause
                </button>
                <button className="flex items-center gap-2 px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors">
                  <RotateCcw className="w-4 h-4" />
                  Restart
                </button>
              </div>
            </div>

            {/* CPU History Chart */}
            <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-white mb-4">CPU Usage History</h3>
              <ResponsiveContainer width="100%" height={250}>
                <LineChart data={cpuHistory}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#475569" />
                  <XAxis dataKey="time" stroke="#94a3b8" />
                  <YAxis stroke="#94a3b8" />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #475569' }}
                    labelStyle={{ color: '#e2e8f0' }}
                  />
                  <Line type="monotone" dataKey="cpu" stroke="#3b82f6" strokeWidth={2} dot={false} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}
      </div>

      {/* All Workers Summary */}
      <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-6">
        <h2 className="text-lg font-semibold text-white mb-4">All Workers Summary</h2>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-600">
                <th className="text-left py-3 px-4 text-slate-300 font-medium">Worker</th>
                <th className="text-left py-3 px-4 text-slate-300 font-medium">Status</th>
                <th className="text-left py-3 px-4 text-slate-300 font-medium">CPU</th>
                <th className="text-left py-3 px-4 text-slate-300 font-medium">RAM</th>
                <th className="text-left py-3 px-4 text-slate-300 font-medium">Queue</th>
              </tr>
            </thead>
            <tbody>
              {workers.map(worker => (
                <tr key={worker.id} className="border-b border-slate-700 hover:bg-slate-700/30 transition-colors">
                  <td className="py-3 px-4 font-medium text-white capitalize">{worker.id}</td>
                  <td className="py-3 px-4">
                    <span className={`text-xs px-2 py-1 rounded capitalize ${
                      worker.status === 'busy' ? 'bg-yellow-900 text-yellow-200' :
                      worker.status === 'idle' ? 'bg-emerald-900 text-emerald-200' :
                      'bg-slate-900 text-slate-200'
                    }`}>{worker.status}</span>
                  </td>
                  <td className="py-3 px-4 text-blue-300">{worker.cpu.toFixed(1)}%</td>
                  <td className="py-3 px-4 text-purple-300">{worker.ram}MB</td>
                  <td className="py-3 px-4 font-medium text-white">{worker.queue}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
