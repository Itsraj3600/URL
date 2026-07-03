'use client'

import { StatsCard } from '@/components/dashboard/stats-card'
import { AreaChartCard, BarChartCard, LineChartCard, PieChartCard } from '@/components/dashboard/charts'
import { RecentActivity } from '@/components/dashboard/recent-activity'
import { QuickActions } from '@/components/dashboard/quick-actions'
import {
  Files,
  Users,
  Radio,
  HardDrive,
  TrendingUp,
  Activity,
  Crown,
  Ban
} from 'lucide-react'

const stats = [
  {
    title: 'Total Files',
    value: '45,231',
    description: 'from last month',
    icon: Files,
    trend: { value: 12.5, isPositive: true },
  },
  {
    title: 'Total Users',
    value: '8,549',
    description: 'active users',
    icon: Users,
    trend: { value: 8.2, isPositive: true },
  },
  {
    title: 'Connected Channels',
    value: '24',
    description: 'active channels',
    icon: Radio,
    trend: { value: 2, isPositive: true },
  },
  {
    title: 'Storage Used',
    value: '1.2 TB',
    description: 'of 2 TB',
    icon: HardDrive,
    trend: { value: 5.1, isPositive: false },
  },
  {
    title: 'Daily Searches',
    value: '12,453',
    description: 'today',
    icon: TrendingUp,
    trend: { value: 15.3, isPositive: true },
  },
  {
    title: 'Avg. Response Time',
    value: '45ms',
    description: 'last 24h',
    icon: Activity,
    trend: { value: 8, isPositive: true },
  },
  {
    title: 'Premium Users',
    value: '124',
    description: 'active subscriptions',
    icon: Crown,
    trend: { value: 20, isPositive: true },
  },
  {
    title: 'Banned Users',
    value: '34',
    description: 'total banned',
    icon: Ban,
    trend: { value: 5, isPositive: false },
  },
]

const userGrowthData = [
  { name: 'Jan', value: 1200 },
  { name: 'Feb', value: 1800 },
  { name: 'Mar', value: 2400 },
  { name: 'Apr', value: 3100 },
  { name: 'May', value: 4200 },
  { name: 'Jun', value: 5100 },
  { name: 'Jul', value: 6500 },
  { name: 'Aug', value: 7200 },
  { name: 'Sep', value: 8000 },
  { name: 'Oct', value: 8200 },
  { name: 'Nov', value: 8500 },
  { name: 'Dec', value: 8549 },
]

const fileTypeData = [
  { name: 'Videos', value: 35000 },
  { name: 'Audio', value: 8000 },
  { name: 'Documents', value: 1500 },
  { name: 'Others', value: 731 },
]

const searchTrendsData = [
  { name: 'Mon', searches: 2400, downloads: 1200 },
  { name: 'Tue', searches: 1398, downloads: 900 },
  { name: 'Wed', searches: 9800, downloads: 3000 },
  { name: 'Thu', searches: 3908, downloads: 2000 },
  { name: 'Fri', searches: 4800, downloads: 2181 },
  { name: 'Sat', searches: 3800, downloads: 2500 },
  { name: 'Sun', searches: 4300, downloads: 2100 },
]

const channelFilesData = [
  { name: 'CINE3600', value: 15000 },
  { name: 'MovieWorld', value: 12000 },
  { name: 'SeriesHub', value: 8000 },
  { name: 'KidsZone', value: 5500 },
  { name: 'Others', value: 4731 },
]

export default function DashboardPage() {
  return (
    <div className="space-y-6">
      {/* Page header */}
      <div>
        <h1 className="text-2xl font-bold text-white">Dashboard</h1>
        <p className="text-slate-400 mt-1">Welcome back! Here&apos;s an overview of your platform.</p>
      </div>

      {/* Stats grid */}
      <div className="grid gap-4 grid-cols-1 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat, index) => (
          <StatsCard key={index} {...stat} />
        ))}
      </div>

      {/* Charts row */}
      <div className="grid gap-6 lg:grid-cols-2">
        <AreaChartCard title="User Growth" data={userGrowthData} />
        <BarChartCard title="File Types Distribution" data={fileTypeData} />
      </div>

      {/* Second charts row */}
      <div className="grid gap-6 lg:grid-cols-3">
        <LineChartCard
          title="Search & Download Trends"
          data={searchTrendsData}
          lines={[{ dataKey: 'searches', color: '#06b6d4' }, { dataKey: 'downloads', color: '#3b82f6' }]}
        />
        <PieChartCard title="Files by Channel" data={channelFilesData} />
      </div>

      {/* Activity and actions row */}
      <div className="grid gap-6 lg:grid-cols-2">
        <RecentActivity />
        <QuickActions />
      </div>
    </div>
  )
}
