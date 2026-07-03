'use client'

import { Sidebar } from './sidebar'
import { TopNav } from './top-nav'

export function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-slate-950">
      <Sidebar />
      <div className="lg:pl-72">
        <TopNav />
        <main className="p-4 lg:p-6">
          {children}
        </main>
      </div>
    </div>
  )
}
