'use client';

import { LucideIcon } from 'lucide-react';

interface StatCardProps {
  label: string;
  value: string | number;
  icon: LucideIcon;
  trend?: number;
  status?: 'online' | 'offline' | 'warning';
}

export function StatCard({ label, value, icon: Icon, trend, status }: StatCardProps) {
  const statusColor = {
    online: 'bg-emerald-500',
    offline: 'bg-red-500',
    warning: 'bg-amber-500',
  };

  return (
    <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-6 hover:border-slate-600 transition-colors">
      <div className="flex items-center justify-between mb-4">
        <p className="text-sm font-medium text-slate-400">{label}</p>
        {status && <div className={`w-2 h-2 rounded-full ${statusColor[status]}`} />}
      </div>
      <div className="flex items-end justify-between">
        <div>
          <p className="text-2xl font-bold text-white">{value}</p>
          {trend !== undefined && (
            <p className={`text-xs mt-2 ${trend >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
              {trend >= 0 ? '+' : ''}{trend}% from yesterday
            </p>
          )}
        </div>
        <Icon className="w-8 h-8 text-slate-500 opacity-50" />
      </div>
    </div>
  );
}
