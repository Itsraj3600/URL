'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Label } from '@/components/ui/label'
import { Switch } from '@/components/ui/switch'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Badge } from '@/components/ui/badge'
import {
  Settings,
  Bot,
  Link,
  Database,
  Shield,
  Bell,
  Save,
  RefreshCw,
} from 'lucide-react'

export default function SettingsPage() {
  const [isLoading, setIsLoading] = useState(false)

  return (
    <div className="space-y-6">
      {/* Page header */}
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Settings</h1>
          <p className="text-slate-400 mt-1">Manage your bot and platform settings</p>
        </div>
        <Button className="bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700 text-white">
          <Save className="mr-2 h-4 w-4" />
          Save Changes
        </Button>
      </div>

      {/* Settings tabs */}
      <Tabs defaultValue="general" className="space-y-6">
        <TabsList className="bg-slate-800/50 border border-slate-700">
          <TabsTrigger value="general" className="data-[state=active]:bg-cyan-500/20 data-[state=active]:text-cyan-400">
            <Settings className="mr-2 h-4 w-4" />
            General
          </TabsTrigger>
          <TabsTrigger value="bot" className="data-[state=active]:bg-cyan-500/20 data-[state=active]:text-cyan-400">
            <Bot className="mr-2 h-4 w-4" />
            Bot
          </TabsTrigger>
          <TabsTrigger value="shortlink" className="data-[state=active]:bg-cyan-500/20 data-[state=active]:text-cyan-400">
            <Link className="mr-2 h-4 w-4" />
            Shortlink
          </TabsTrigger>
          <TabsTrigger value="database" className="data-[state=active]:bg-cyan-500/20 data-[state=active]:text-cyan-400">
            <Database className="mr-2 h-4 w-4" />
            Database
          </TabsTrigger>
          <TabsTrigger value="security" className="data-[state=active]:bg-cyan-500/20 data-[state=active]:text-cyan-400">
            <Shield className="mr-2 h-4 w-4" />
            Security
          </TabsTrigger>
        </TabsList>

        <TabsContent value="general" className="space-y-6">
          <div className="grid gap-6 lg:grid-cols-2">
            <Card className="border-slate-700/50 bg-slate-800/50 backdrop-blur-xl">
              <CardHeader>
                <CardTitle className="text-base font-medium text-white">Admin Settings</CardTitle>
                <CardDescription className="text-slate-400">Configure admin list and permissions</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label className="text-slate-300">Admin IDs</Label>
                  <Input
                    placeholder="Enter Telegram user IDs (space separated)"
                    className="bg-slate-900/50 border-slate-700 text-white"
                  />
                  <p className="text-xs text-slate-500">Separate multiple IDs with spaces</p>
                </div>
                <div className="space-y-2">
                  <Label className="text-slate-300">Log Channel ID</Label>
                  <Input
                    placeholder="-1001234567890"
                    className="bg-slate-900/50 border-slate-700 text-white"
                  />
                </div>
                <div className="space-y-2">
                  <Label className="text-slate-300">Support Group Link</Label>
                  <Input
                    placeholder="https://t.me/yourgroup"
                    className="bg-slate-900/50 border-slate-700 text-white"
                  />
                </div>
              </CardContent>
            </Card>

            <Card className="border-slate-700/50 bg-slate-800/50 backdrop-blur-xl">
              <CardHeader>
                <CardTitle className="text-base font-medium text-white">Force Subscription</CardTitle>
                <CardDescription className="text-slate-400">Require users to join channels</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label className="text-slate-300">Enable Force Sub</Label>
                    <p className="text-xs text-slate-500">Require users to join channels before using bot</p>
                  </div>
                  <Switch defaultChecked />
                </div>
                <div className="space-y-2">
                  <Label className="text-slate-300">Channel ID</Label>
                  <Input
                    placeholder="-1001234567890"
                    className="bg-slate-900/50 border-slate-700 text-white"
                  />
                </div>
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label className="text-slate-300">Check Join Requests</Label>
                    <p className="text-xs text-slate-500">For private channels with request mode</p>
                  </div>
                  <Switch />
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="bot" className="space-y-6">
          <Card className="border-slate-700/50 bg-slate-800/50 backdrop-blur-xl">
            <CardHeader>
              <CardTitle className="text-base font-medium text-white">Bot Configuration</CardTitle>
              <CardDescription className="text-slate-400">Core bot settings and behavior</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid gap-4 lg:grid-cols-2">
                <div className="space-y-2">
                  <Label className="text-slate-300">API_ID</Label>
                  <Input
                    type="password"
                    value="•••••••••••"
                    readOnly
                    className="bg-slate-900/50 border-slate-700 text-white"
                  />
                </div>
                <div className="space-y-2">
                  <Label className="text-slate-300">API_HASH</Label>
                  <Input
                    type="password"
                    value="••••••••••••••••"
                    readOnly
                    className="bg-slate-900/50 border-slate-700 text-white"
                  />
                </div>
              </div>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label className="text-slate-300">IMDB Integration</Label>
                    <p className="text-xs text-slate-500">Show IMDB info for movie searches</p>
                  </div>
                  <Switch defaultChecked />
                </div>
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label className="text-slate-300">Auto File Filtering</Label>
                    <p className="text-xs text-slate-500">Automatically filter files by quality</p>
                  </div>
                  <Switch defaultChecked />
                </div>
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label className="text-slate-300">Spell Check</Label>
                    <p className="text-xs text-slate-500">Suggest corrections for misspelled queries</p>
                  </div>
                  <Switch defaultChecked />
                </div>
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label className="text-slate-300">Welcome Messages</Label>
                    <p className="text-xs text-slate-500">Send welcome message to new users</p>
                  </div>
                  <Switch defaultChecked />
                </div>
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label className="text-slate-300">Auto Delete</Label>
                    <p className="text-xs text-slate-500">Auto delete files after specified time</p>
                  </div>
                  <Switch />
                </div>
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label className="text-slate-300">Protect Content</Label>
                    <p className="text-xs text-slate-500">Prevent forwarding of bot content</p>
                  </div>
                  <Switch defaultChecked />
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="shortlink" className="space-y-6">
          <Card className="border-slate-700/50 bg-slate-800/50 backdrop-blur-xl">
            <CardHeader>
              <CardTitle className="text-base font-medium text-white">Shortlink Settings</CardTitle>
              <CardDescription className="text-slate-400">Configure URL shortener integration</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid gap-4 lg:grid-cols-2">
                <div className="space-y-2">
                  <Label className="text-slate-300">Shortlink Domain</Label>
                  <Input
                    placeholder="e.g. instantearn.in"
                    className="bg-slate-900/50 border-slate-700 text-white"
                  />
                </div>
                <div className="space-y-2">
                  <Label className="text-slate-300">API Key</Label>
                  <Input
                    type="password"
                    placeholder="Your shortlink API key"
                    className="bg-slate-900/50 border-slate-700 text-white"
                  />
                </div>
              </div>
              <div className="space-y-2">
                <Label className="text-slate-300">Tutorial Link</Label>
                <Input
                  placeholder="https://t.me/yourtutorial"
                  className="bg-slate-900/50 border-slate-700 text-white"
                />
                <p className="text-xs text-slate-500">Link to tutorial on how to open shortlinks</p>
              </div>
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label className="text-slate-300">Enable Shortlink</Label>
                  <p className="text-xs text-slate-500">Apply shortlinks to file downloads</p>
                </div>
                <Switch defaultChecked />
              </div>
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label className="text-slate-300">Shortlink for Premium</Label>
                    <p className="text-xs text-slate-500">Apply shortlinks even for premium users</p>
                </div>
                <Switch />
              </div>
            </CardContent>
          </Card>

          <Card className="border-slate-700/50 bg-slate-800/50 backdrop-blur-xl">
            <CardHeader>
              <CardTitle className="text-base font-medium text-white">Stream Settings</CardTitle>
              <CardDescription className="text-slate-400">Configure streaming server</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label className="text-slate-300">Stream Site</Label>
                <Input
                  placeholder="ziplinker.net"
                  className="bg-slate-900/50 border-slate-700 text-white"
                />
              </div>
              <div className="space-y-2">
                <Label className="text-slate-300">Stream API Key</Label>
                <Input
                  type="password"
                  placeholder="Your stream API key"
                  className="bg-slate-900/50 border-slate-700 text-white"
                />
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="database" className="space-y-6">
          <Card className="border-slate-700/50 bg-slate-800/50 backdrop-blur-xl">
            <CardHeader>
              <CardTitle className="text-base font-medium text-white">Database Configuration</CardTitle>
              <CardDescription className="text-slate-400">Supabase database settings</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="bg-slate-700/30 rounded-xl p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-white font-medium">Supabase PostgreSQL</p>
                    <p className="text-slate-400 text-sm">sliycmaxapvrlooihxgp.supabase.co</p>
                  </div>
                  <Badge className="bg-emerald-500/20 text-emerald-400">Connected</Badge>
                </div>
              </div>
              <Button variant="outline" className="border-slate-700 text-slate-300 hover:bg-slate-700 hover:text-white">
                <RefreshCw className="mr-2 h-4 w-4" />
                Test Connection
              </Button>
            </CardContent>
          </Card>

          <Card className="border-slate-700/50 bg-slate-800/50 backdrop-blur-xl">
            <CardHeader>
              <CardTitle className="text-base font-medium text-white">Backup Settings</CardTitle>
              <CardDescription className="text-slate-400">Configure automatic backups</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label className="text-slate-300">Automatic Backups</Label>
                  <p className="text-xs text-slate-500">Daily database backups at 00:00 UTC</p>
                </div>
                <Switch defaultChecked />
              </div>
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label className="text-slate-300">Retain Backups</Label>
                </div>
                <select className="bg-slate-900/50 border border-slate-700 rounded-md p-2 text-white">
                  <option>7 days</option>
                  <option>30 days</option>
                  <option>90 days</option>
                </select>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="security" className="space-y-6">
          <Card className="border-slate-700/50 bg-slate-800/50 backdrop-blur-xl">
            <CardHeader>
              <CardTitle className="text-base font-medium text-white">Security Settings</CardTitle>
              <CardDescription className="text-slate-400">Configure security and rate limiting</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label className="text-slate-300">Rate Limiting</Label>
                  <p className="text-xs text-slate-500">Limit requests per user</p>
                </div>
                <Switch defaultChecked />
              </div>
              <div className="space-y-2">
                <Label className="text-slate-300">Max Requests per Minute</Label>
                <Input
                  type="number"
                  defaultValue="10"
                  className="bg-slate-900/50 border-slate-700 text-white"
                />
              </div>
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label className="text-slate-300">Delete CamRip/PreDVD</Label>
                  <p className="text-xs text-slate-500">Auto-delete low quality files</p>
                </div>
                <Switch defaultChecked />
              </div>
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label className="text-slate-300">Block Forwarding</Label>
                    <p className="text-xs text-slate-500">Prevent forwarded content from being indexed</p>
                </div>
                <Switch />
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
