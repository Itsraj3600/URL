'use client';

import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { LayoutDashboard, Users, Zap, Users2, TrendingUp, MessageSquare, BarChart3, FileText, Activity, Settings, LogOut } from 'lucide-react';

const navItems = [
  { href: '/admin/dashboard/overview', label: 'Overview', icon: LayoutDashboard },
  { href: '/admin/dashboard/workers', label: 'Workers', icon: Zap },
  { href: '/admin/dashboard/indexing', label: 'Indexing', icon: Activity },
  { href: '/admin/dashboard/users', label: 'Users', icon: Users },
  { href: '/admin/dashboard/search', label: 'Search', icon: TrendingUp },
  { href: '/admin/dashboard/channels', label: 'Channels', icon: MessageSquare },
  { href: '/admin/dashboard/analytics', label: 'Analytics', icon: BarChart3 },
  { href: '/admin/dashboard/logs', label: 'Logs', icon: FileText },
  { href: '/admin/dashboard/health', label: 'Health', icon: Activity },
  { href: '/admin/dashboard/settings', label: 'Settings', icon: Settings },
];

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();

  const handleLogout = () => {
    localStorage.removeItem('adminToken');
    router.push('/admin/login');
  };

  return (
    <div className="flex h-screen bg-slate-950">
      {/* Sidebar */}
      <div className="w-64 bg-slate-900 border-r border-slate-700 overflow-y-auto">
        <div className="p-6">
          <h1 className="text-2xl font-bold text-white">CINE3600</h1>
          <p className="text-xs text-slate-500 mt-1">Admin Dashboard</p>
        </div>

        <nav className="mt-8 px-3">
          {navItems.map(item => {
            const Icon = item.icon;
            const isActive = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center gap-3 px-4 py-3 rounded-lg mb-2 transition-colors ${
                  isActive
                    ? 'bg-blue-600/20 text-blue-400 border border-blue-600'
                    : 'text-slate-400 hover:bg-slate-800/50'
                }`}
              >
                <Icon className="w-5 h-5" />
                <span>{item.label}</span>
              </Link>
            );
          })}
        </nav>

        <div className="absolute bottom-6 left-3 right-3">
          <button
            onClick={handleLogout}
            className="w-full flex items-center gap-2 px-4 py-2 bg-red-900/20 text-red-400 rounded-lg hover:bg-red-900/30 transition-colors text-sm"
          >
            <LogOut className="w-4 h-4" />
            Logout
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-auto bg-slate-950">
        {children}
      </div>
    </div>
  );
}
