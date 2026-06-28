'use client';

import { useEffect, useState } from 'react';
import { fetchIndexJobs, IndexJob } from '@/lib/dashboard-api';
import { Pause, Play, X } from 'lucide-react';

export default function IndexingPage() {
  const [jobs, setJobs] = useState<IndexJob[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadData = async () => {
      try {
        const data = await fetchIndexJobs();
        setJobs(data);
      } catch (error) {
        console.error('[v0] Failed to load indexing jobs:', error);
      } finally {
        setLoading(false);
      }
    };

    loadData();
    const interval = setInterval(loadData, 2000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="space-y-6 p-8">
      <div>
        <h1 className="text-3xl font-bold text-white">Index Manager</h1>
        <p className="text-slate-400 mt-1">Manage content indexing jobs</p>
      </div>

      <div className="space-y-4">
        {jobs.map(job => (
          <div key={job.id} className="bg-slate-800/50 border border-slate-700 rounded-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-white capitalize">{job.type}</h3>
              <span className="text-sm text-slate-400">{job.progress.toFixed(1)}%</span>
            </div>

            {/* Progress Bar */}
            <div className="mb-4">
              <div className="w-full bg-slate-700 rounded-full h-2 overflow-hidden">
                <div
                  className="bg-blue-500 h-full transition-all duration-300"
                  style={{ width: `${job.progress}%` }}
                />
              </div>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4 text-sm">
              <div>
                <p className="text-slate-400">ETA</p>
                <p className="text-white font-medium">{Math.floor(job.eta / 60)}m</p>
              </div>
              <div>
                <p className="text-slate-400">Speed</p>
                <p className="text-white font-medium">{job.speed.toFixed(0)}/s</p>
              </div>
              <div>
                <p className="text-slate-400">Duplicates</p>
                <p className="text-yellow-400 font-medium">{job.duplicates}</p>
              </div>
              <div>
                <p className="text-slate-400">Errors</p>
                <p className="text-red-400 font-medium">{job.errors}</p>
              </div>
            </div>

            {/* Actions */}
            <div className="flex gap-2">
              <button className="flex items-center gap-2 px-3 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm rounded transition-colors">
                <Play className="w-4 h-4" />
                Resume
              </button>
              <button className="flex items-center gap-2 px-3 py-2 bg-amber-600 hover:bg-amber-700 text-white text-sm rounded transition-colors">
                <Pause className="w-4 h-4" />
                Pause
              </button>
              <button className="flex items-center gap-2 px-3 py-2 bg-red-600 hover:bg-red-700 text-white text-sm rounded transition-colors">
                <X className="w-4 h-4" />
                Cancel
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
