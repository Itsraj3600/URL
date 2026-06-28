'use client';

import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

const trendData = [
  { day: 'Mon', searches: 240, downloads: 120 },
  { day: 'Tue', searches: 320, downloads: 180 },
  { day: 'Wed', searches: 280, downloads: 150 },
  { day: 'Thu', searches: 350, downloads: 200 },
  { day: 'Fri', searches: 420, downloads: 250 },
  { day: 'Sat', searches: 480, downloads: 290 },
  { day: 'Sun', searches: 410, downloads: 260 },
];

const deviceData = [
  { name: 'Mobile', value: 65 },
  { name: 'Desktop', value: 25 },
  { name: 'Tablet', value: 10 },
];

const COLORS = ['#3b82f6', '#8b5cf6', '#ec4899'];

export default function AnalyticsPage() {
  return (
    <div className="space-y-6 p-8">
      <div>
        <h1 className="text-3xl font-bold text-white">Analytics</h1>
        <p className="text-slate-400 mt-1">Detailed usage and trends</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-6">
          <p className="text-sm text-slate-400 mb-1">Avg Searches/Day</p>
          <p className="text-3xl font-bold text-blue-400">350</p>
        </div>
        <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-6">
          <p className="text-sm text-slate-400 mb-1">Avg Downloads/Day</p>
          <p className="text-3xl font-bold text-purple-400">200</p>
        </div>
        <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-6">
          <p className="text-sm text-slate-400 mb-1">Active Users</p>
          <p className="text-3xl font-bold text-green-400">12.4K</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Week Trend */}
        <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-6">
          <h2 className="text-lg font-semibold text-white mb-4">Weekly Trend</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={trendData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#475569" />
              <XAxis dataKey="day" stroke="#94a3b8" />
              <YAxis stroke="#94a3b8" />
              <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #475569' }} />
              <Legend wrapperStyle={{ paddingTop: '20px' }} />
              <Bar dataKey="searches" fill="#3b82f6" />
              <Bar dataKey="downloads" fill="#8b5cf6" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Device Breakdown */}
        <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-6">
          <h2 className="text-lg font-semibold text-white mb-4">Device Breakdown</h2>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie data={deviceData} cx="50%" cy="50%" labelLine={false} label={({ name, value }) => `${name} ${value}%`} outerRadius={80} fill="#8884d8" dataKey="value">
                {deviceData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #475569' }} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
