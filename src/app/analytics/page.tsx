'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { AreaChartCard, BarChartCard, LineChartCard, PieChartCard } from '@/components/dashboard/charts'
import { StatsCard } from '@/components/dashboard/stats-card'
import { TrendingUp, Search, Download, Users, Clock } from 'lucide-react'

const userGrowthData = [
  { name: 'Jan', value: 1200 }, { name: 'Feb', value: 1800 }, { name: 'Mar', value: 2400 },
  { name: 'Apr', value: 3100 }, { name: 'May', value: 4200 }, { name: 'Jun', value: 5100 },
  { name: 'Jul', value: 6500 }, { name: 'Aug', value: 7200 }, { name: 'Sep', value: 8000 },
  { name: 'Oct', value: 8200 }, { name: 'Nov', value: 8500 }, { name: 'Dec', value: 8549 },
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

const topMoviesData = [
  { name: 'Oppenheimer', value: 1234 }, { name: 'Interstellar', value: 987 },
  { name: 'Dark Knight', value: 876 }, { name: 'Dune', value: 765 },
  { name: 'Prey', value: 543 },
]

const fileSizeData = [
  { name: '< 1 GB', value: 5000 }, { name: '1-5 GB', value: 15000 },
  { name: '5-10 GB', value: 12000 }, { name: '> 10 GB', value: 5000 },
]

const topLanguagesData = [
  { name: 'Hindi', value: 15000 }, { name: 'English', value: 12000 },
  { name: 'Tamil', value: 8000 }, { name: 'Telugu', value: 6500 },
  { name: 'Malayalam', value: 4000 },
]

const responseTimeData = [
  { name: '00:00', value: 45 }, { name: '04:00', value: 52 },
  { name: '08:00', value: 48 }, { name: '12:00', value: 55 },
  { name: '16:00', value: 47 }, { name: '20:00', value: 43 },
]

export default function AnalyticsPage() {
  return (
    <div className="space-y-6">
      {/* Page header */}
      <div>
        <h1 className="text-2xl font-bold text-white">Analytics</h1>
        <p className="text-slate-400 mt-1">Detailed insights and statistics about your platform</p>
      </div>

      {/* Key metrics */}
      <div className="grid gap-4 grid-cols-1 sm:grid-cols-2 lg:grid-cols-4">
        <StatsCard title="Total Searches" value="1.2M" icon={Search} trend={{ value: 15.3, isPositive: true }} />
        <StatsCard title="Total Downloads" value="845K" icon={Download} trend={{ value: 12.1, isPositive: true }} />
        <StatsCard title="Active Users" value="2,345" icon={Users} trend={{ value: 8.5, isPositive: true }} />
        <StatsCard title="Avg Response" value="45ms" icon={Clock} trend={{ value: 5, isPositive: true }} />
      </div>

      {/* Tabs for different views */}
      <Tabs defaultValue="overview" className="space-y-6">
        <TabsList className="bg-slate-800/50 border border-slate-700">
          <TabsTrigger value="overview" className="data-[state=active]:bg-cyan-500/20 data-[state=active]:text-cyan-400">Overview</TabsTrigger>
          <TabsTrigger value="searches" className="data-[state=active]:bg-cyan-500/20 data-[state=active]:text-cyan-400">Searches</TabsTrigger>
          <TabsTrigger value="content" className="data-[state=active]:bg-cyan-500/20 data-[state=active]:text-cyan-400">Content</TabsTrigger>
          <TabsTrigger value="performance" className="data-[state=active]:bg-cyan-500/20 data-[state=active]:text-cyan-400">Performance</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          <div className="grid gap-6 lg:grid-cols-2">
            <AreaChartCard title="User Growth" data={userGrowthData} />
            <LineChartCard
              title="Search & Download Trends"
              data={searchTrendsData}
              lines={[{ dataKey: 'searches', color: '#06b6d4' }, { dataKey: 'downloads', color: '#3b82f6' }]}
            />
          </div>
          <div className="grid gap-6 lg:grid-cols-2">
            <PieChartCard title="File Distribution by Language" data={topLanguagesData} />
            <BarChartCard title="Top Searched Movies" data={topMoviesData} />
          </div>
        </TabsContent>

        <TabsContent value="searches" className="space-y-6">
          <div className="grid gap-6 lg:grid-cols-2">
            <LineChartCard
              title="Daily Search Volume"
              data={searchTrendsData}
              lines={[{ dataKey: 'searches', color: '#06b6d4' }]}
            />
            <BarChartCard title="Top Searched Movies" data={topMoviesData} />
          </div>
          <Card className="border-slate-700/50 bg-slate-800/50 backdrop-blur-xl">
            <CardHeader>
              <CardTitle className="text-base font-medium text-white">Search Analytics</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-3">
                <div className="bg-slate-700/30 rounded-xl p-4">
                  <p className="text-slate-400 text-sm">Most Searched Today</p>
                  <p className="text-white font-bold text-lg mt-1">Oppenheimer</p>
                  <p className="text-cyan-400 text-sm">1,234 searches</p>
                </div>
                <div className="bg-slate-700/30 rounded-xl p-4">
                  <p className="text-slate-400 text-sm">Avg. Results/Search</p>
                  <p className="text-white font-bold text-lg mt-1">8.5 files</p>
                  <p className="text-emerald-400 text-sm">+12% from last week</p>
                </div>
                <div className="bg-slate-700/30 rounded-xl p-4">
                  <p className="text-slate-400 text-sm">No-Result Rate</p>
                  <p className="text-white font-bold text-lg mt-1">3.2%</p>
                  <p className="text-emerald-400 text-sm">-5% from last week</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="content" className="space-y-6">
          <div className="grid gap-6 lg:grid-cols-2">
            <PieChartCard title="File Size Distribution" data={fileSizeData} />
            <PieChartCard title="Content by Language" data={topLanguagesData} />
          </div>
          <Card className="border-slate-700/50 bg-slate-800/50 backdrop-blur-xl">
            <CardHeader>
              <CardTitle className="text-base font-medium text-white">Content Categories</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-4">
                <div className="bg-gradient-to-br from-cyan-500/20 to-blue-600/20 rounded-xl p-4 border border-cyan-500/20">
                  <p className="text-2xl font-bold text-white">35,542</p>
                  <p className="text-slate-400 text-sm">Movies</p>
                </div>
                <div className="bg-gradient-to-br from-purple-500/20 to-pink-600/20 rounded-xl p-4 border border-purple-500/20">
                  <p className="text-2xl font-bold text-white">5,893</p>
                  <p className="text-slate-400 text-sm">TV Series</p>
                </div>
                <div className="bg-gradient-to-br from-emerald-500/20 to-teal-600/20 rounded-xl p-4 border border-emerald-500/20">
                  <p className="text-2xl font-bold text-white">2,456</p>
                  <p className="text-slate-400 text-sm">Documentaries</p>
                </div>
                <div className="bg-gradient-to-br from-amber-500/20 to-orange-600/20 rounded-xl p-4 border border-amber-500/20">
                  <p className="text-2xl font-bold text-white">1,340</p>
                  <p className="text-slate-400 text-sm">Anime</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="performance" className="space-y-6">
          <div className="grid gap-6 lg:grid-cols-2">
            <LineChartCard
              title="API Response Time (ms)"
              data={responseTimeData}
              lines={[{ dataKey: 'value', color: '#06b6d4' }]}
            />
            <Card className="border-slate-700/50 bg-slate-800/50 backdrop-blur-xl">
              <CardHeader>
                <CardTitle className="text-base font-medium text-white">System Health</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-slate-400">Database</span>
                    <span className="text-emerald-400 font-medium">Healthy</span>
                  </div>
                  <div className="h-2 bg-slate-700 rounded-full overflow-hidden">
                    <div className="h-full bg-emerald-500" style={{ width: '95%' }} />
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-slate-400">API Latency</span>
                    <span className="text-emerald-400 font-medium">45ms avg</span>
                  </div>
                  <div className="h-2 bg-slate-700 rounded-full overflow-hidden">
                    <div className="h-full bg-cyan-500" style={{ width: '98%' }} />
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-slate-400">Uptime</span>
                    <span className="text-emerald-400 font-medium">99.9%</span>
                  </div>
                  <div className="h-2 bg-slate-700 rounded-full overflow-hidden">
                    <div className="h-full bg-emerald-500" style={{ width: '99.9%' }} />
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  )
}
