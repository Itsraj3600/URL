'use client';

import { useEffect, useState } from 'react';
import { fetchSearchAnalytics, fetchTopMovies, SearchAnalytic, TopMovie } from '@/lib/dashboard-api';
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';

export default function SearchPage() {
  const [analytics, setAnalytics] = useState<SearchAnalytic[]>([]);
  const [topMovies, setTopMovies] = useState<TopMovie[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadData = async () => {
      try {
        const [analyticsData, moviesData] = await Promise.all([
          fetchSearchAnalytics(),
          fetchTopMovies(10),
        ]);
        
        const chartData = analyticsData.map(a => ({
          time: a.timestamp.getHours() + ':00',
          searches: a.searches,
        }));
        setAnalytics(chartData);
        setTopMovies(moviesData);
      } catch (error) {
        console.error('[v0] Failed to load search analytics:', error);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, []);

  return (
    <div className="space-y-6 p-8">
      <div>
        <h1 className="text-3xl font-bold text-white">Search Analytics</h1>
        <p className="text-slate-400 mt-1">Analyze search patterns and trends</p>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Search Trend */}
        <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-6">
          <h2 className="text-lg font-semibold text-white mb-4">Searches/Hour (Last 24h)</h2>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={analytics}>
              <CartesianGrid strokeDasharray="3 3" stroke="#475569" />
              <XAxis dataKey="time" stroke="#94a3b8" />
              <YAxis stroke="#94a3b8" />
              <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #475569' }} />
              <Line type="monotone" dataKey="searches" stroke="#3b82f6" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Failed Searches */}
        <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-6">
          <h2 className="text-lg font-semibold text-white mb-4">Search Results</h2>
          <div className="space-y-3">
            <div className="flex items-center justify-between p-3 bg-slate-700/50 rounded">
              <span className="text-slate-300">Successful Searches</span>
              <span className="text-green-400 font-bold text-lg">94.2%</span>
            </div>
            <div className="flex items-center justify-between p-3 bg-slate-700/50 rounded">
              <span className="text-slate-300">Failed Searches</span>
              <span className="text-red-400 font-bold text-lg">5.8%</span>
            </div>
            <div className="flex items-center justify-between p-3 bg-slate-700/50 rounded">
              <span className="text-slate-300">Cache Hit Rate</span>
              <span className="text-blue-400 font-bold text-lg">87.3%</span>
            </div>
          </div>
        </div>
      </div>

      {/* Top Movies */}
      <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-6">
        <h2 className="text-lg font-semibold text-white mb-4">Top 10 Searched Movies</h2>
        <div className="space-y-2">
          {topMovies.map((movie, i) => (
            <div key={i} className="flex items-center justify-between p-3 bg-slate-700/30 rounded hover:bg-slate-700/50 transition-colors">
              <div className="flex items-center gap-3">
                <span className="text-slate-500 font-bold w-6 text-right">#{i + 1}</span>
                <div>
                  <p className="text-white font-medium">{movie.title}</p>
                  <p className="text-xs text-slate-400">{movie.downloads} downloads</p>
                </div>
              </div>
              <span className="text-blue-400 font-bold">{movie.searches.toLocaleString()} searches</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
