'use client'

import { useState } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'

const navigation = [
  { name: 'Overview', href: '/dashboard', icon: '📊' },
  { name: 'Users', href: '/dashboard/users', icon: '👥' },
  { name: 'Indexing', href: '/dashboard/indexing', icon: '📁' },
  { name: 'Analytics', href: '/dashboard/analytics', icon: '📈' },
  { name: 'Channels', href: '/dashboard/channels', icon: '📡' },
  { name: 'Database', href: '/dashboard/database', icon: '🗄️' },
  { name: 'Cache', href: '/dashboard/cache', icon: '⚡' },
  { name: 'Logs', href: '/dashboard/logs', icon: '📝' },
  { name: 'Health', href: '/dashboard/health', icon: '💚' },
  { name: 'Settings', href: '/dashboard/settings', icon: '⚙️' },
]

export default function DashboardShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname()
  const [sidebarOpen, setSidebarOpen] = useState(true)

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100">
      {/* Sidebar */}
      <aside
        className={`fixed inset-y-0 left-0 z-50 w-64 transform bg-zinc-900 border-r border-zinc-800 transition-transform duration-200 ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        {/* Logo */}
        <div className="flex items-center justify-between h-16 px-4 border-b border-zinc-800">
          <Link href="/dashboard" className="flex items-center gap-2">
            <span className="text-2xl">🎬</span>
            <span className="font-bold text-lg">CINE3600</span>
          </Link>
          <button
            onClick={() => setSidebarOpen(false)}
            className="p-1 rounded hover:bg-zinc-800 lg:hidden"
          >
            ✕
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-3 py-4 space-y-1">
          {navigation.map((item) => {
            const isActive = pathname === item.href
            return (
              <Link
                key={item.name}
                href={item.href}
                className={`flex items-center gap-3 px-3 py-2 rounded-lg transition-colors ${
                  isActive
                    ? 'bg-blue-600/20 text-blue-400'
                    : 'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800'
                }`}
              >
                <span className="text-lg">{item.icon}</span>
                <span>{item.name}</span>
              </Link>
            )
          })}
        </nav>

        {/* Footer */}
        <div className="p-4 border-t border-zinc-800">
          <div className="flex items-center gap-2 text-sm text-zinc-500">
            <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
            <span>System Online</span>
          </div>
        </div>
      </aside>

      {/* Main content */}
      <div className={`${sidebarOpen ? 'lg:ml-64' : ''} transition-all duration-200`}>
        {/* Top bar */}
        <header className="sticky top-0 z-40 h-16 bg-zinc-900/80 backdrop-blur border-b border-zinc-800">
          <div className="flex items-center justify-between h-full px-4">
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="p-2 rounded-lg hover:bg-zinc-800"
            >
              {sidebarOpen ? '◀' : '☰'}
            </button>

            <div className="flex items-center gap-4">
              {/* Search */}
              <div className="relative hidden md:block">
                <input
                  type="text"
                  placeholder="Search..."
                  className="w-64 px-4 py-2 bg-zinc-800 border border-zinc-700 rounded-lg text-sm focus:outline-none focus:border-blue-500"
                />
              </div>

              {/* Status indicators */}
              <div className="flex items-center gap-2">
                <span className="px-2 py-1 text-xs bg-green-500/20 text-green-400 rounded">
                  Bot Online
                </span>
                <span className="px-2 py-1 text-xs bg-zinc-700 text-zinc-300 rounded">
                  DB Healthy
                </span>
              </div>

              {/* User menu */}
              <button className="flex items-center gap-2 p-2 rounded-lg hover:bg-zinc-800">
                <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center">
                  A
                </div>
              </button>
            </div>
          </div>
        </header>

        {/* Page content */}
        <main className="p-6">{children}</main>
      </div>

      {/* Mobile overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}
    </div>
  )
}
