'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger, DialogDescription } from '@/components/ui/dialog'
import { formatRelativeTime } from '@/lib/utils'
import {
  Search,
  MoreHorizontal,
  Ban,
  UserCheck,
  Trash2,
  Users,
  UserPlus,
  Crown,
  Shield,
  Mail,
} from 'lucide-react'
import { motion } from 'framer-motion'

const users = [
  { id: 123456789, name: 'John Doe', username: 'johndoe', isBanned: false, isPremium: true, premiumExpiry: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString(), createdAt: new Date(Date.now() - 90 * 24 * 60 * 60 * 1000).toISOString() },
  { id: 987654321, name: 'Jane Smith', username: 'janesmith', isBanned: false, isPremium: false, premiumExpiry: null, createdAt: new Date(Date.now() - 60 * 24 * 60 * 60 * 1000).toISOString() },
  { id: 456789123, name: 'Movie Fan', username: 'moviefan123', isBanned: false, isPremium: true, premiumExpiry: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString(), createdAt: new Date(Date.now() - 180 * 24 * 60 * 60 * 1000).toISOString() },
  { id: 789123456, name: 'Spam User', username: 'spamuser', isBanned: true, isPremium: false, banReason: 'Spamming', premiumExpiry: null, createdAt: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString() },
  { id: 321654987, name: 'Cinema Lover', username: 'cinemalover', isBanned: false, isPremium: true, premiumExpiry: new Date(Date.now() + 90 * 24 * 60 * 60 * 1000).toISOString(), createdAt: new Date(Date.now() - 45 * 24 * 60 * 60 * 1000).toISOString() },
]

export default function UsersPage() {
  const [searchQuery, setSearchQuery] = useState('')
  const [banDialogOpen, setBanDialogOpen] = useState(false)
  const [premiumDialogOpen, setPremiumDialogOpen] = useState(false)

  return (
    <div className="space-y-6">
      {/* Page header */}
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Users</h1>
          <p className="text-slate-400 mt-1">Manage bot users and premium subscriptions</p>
        </div>
        <div className="flex gap-3">
          <Dialog open={premiumDialogOpen} onOpenChange={setPremiumDialogOpen}>
            <DialogTrigger>
              <Button variant="outline" className="border-slate-700 text-slate-300 hover:bg-slate-700 hover:text-white">
                <Crown className="mr-2 h-4 w-4" />
                Add Premium
              </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-[425px] bg-slate-800 border-slate-700 text-white">
              <DialogHeader>
                <DialogTitle>Add Premium User</DialogTitle>
                <DialogDescription className="text-slate-400">
                  Enter the user ID and select a premium plan.
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4 pt-4">
                <Input placeholder="User ID" className="bg-slate-900/50 border-slate-700" />
                <select className="w-full rounded-md border border-slate-700 bg-slate-900/50 p-2 text-white">
                  <option>Bronze Plan - 7 days (10 INR)</option>
                  <option>Silver Plan - 30 days (30 INR)</option>
                  <option>Gold Plan - 90 days (90 INR)</option>
                  <option>Platinum Plan - 180 days (150 INR)</option>
                  <option>Diamond Plan - 365 days (300 INR)</option>
                </select>
                <Button className="w-full bg-cyan-500 hover:bg-cyan-600">Add Premium</Button>
              </div>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {/* Stats */}
      <div className="grid gap-4 md:grid-cols-4">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          <Card className="border-slate-700/50 bg-slate-800/50 backdrop-blur-xl">
            <CardContent className="pt-6">
              <div className="flex items-center gap-4">
                <div className="bg-cyan-500/20 p-3 rounded-xl">
                  <Users className="h-6 w-6 text-cyan-400" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-white">8,549</p>
                  <p className="text-sm text-slate-400">Total Users</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
          <Card className="border-slate-700/50 bg-slate-800/50 backdrop-blur-xl">
            <CardContent className="pt-6">
              <div className="flex items-center gap-4">
                <div className="bg-amber-500/20 p-3 rounded-xl">
                  <UserPlus className="h-6 w-6 text-amber-400" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-white">234</p>
                  <p className="text-sm text-slate-400">New Today</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
          <Card className="border-slate-700/50 bg-slate-800/50 backdrop-blur-xl">
            <CardContent className="pt-6">
              <div className="flex items-center gap-4">
                <div className="bg-purple-500/20 p-3 rounded-xl">
                  <Crown className="h-6 w-6 text-purple-400" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-white">124</p>
                  <p className="text-sm text-slate-400">Premium Users</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
          <Card className="border-slate-700/50 bg-slate-800/50 backdrop-blur-xl">
            <CardContent className="pt-6">
              <div className="flex items-center gap-4">
                <div className="bg-red-500/20 p-3 rounded-xl">
                  <Shield className="h-6 w-6 text-red-400" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-white">34</p>
                  <p className="text-sm text-slate-400">Banned Users</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Users table */}
      <Card className="border-slate-700/50 bg-slate-800/50 backdrop-blur-xl">
        <CardHeader>
          <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
            <CardTitle className="text-base font-medium text-white">All Users</CardTitle>
            <div className="relative w-full md:w-64">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
              <Input
                placeholder="Search users..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-9 bg-slate-900/50 border-slate-700 text-white"
              />
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="rounded-xl border border-slate-700/50 overflow-hidden">
            <Table>
              <TableHeader>
                <TableRow className="hover:bg-slate-700/30 border-slate-700/50">
                  <TableHead className="text-slate-400">User</TableHead>
                  <TableHead className="text-slate-400">ID</TableHead>
                  <TableHead className="text-slate-400">Status</TableHead>
                  <TableHead className="text-slate-400">Joined</TableHead>
                  <TableHead className="w-[50px]"></TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {users.map((user) => (
                  <TableRow key={user.id} className="hover:bg-slate-700/30 border-slate-700/50">
                    <TableCell>
                      <div className="flex items-center gap-3">
                        <Avatar className="h-9 w-9 border-2 border-cyan-500/50">
                          <AvatarImage src={`https://api.dicebear.com/7.x/avataaars/svg?seed=${user.id}`} />
                          <AvatarFallback className="bg-gradient-to-br from-cyan-500 to-blue-600 text-white">
                            {user.name.split(' ').map(n => n[0]).join('')}
                          </AvatarFallback>
                        </Avatar>
                        <div>
                          <p className="text-white font-medium">{user.name}</p>
                          <p className="text-slate-400 text-xs">@{user.username}</p>
                        </div>
                      </div>
                    </TableCell>
                    <TableCell>
                      <code className="text-slate-400 text-sm">{user.id}</code>
                    </TableCell>
                    <TableCell>
                      <div className="flex gap-2">
                        {user.isBanned ? (
                          <Badge className="bg-red-500/20 text-red-400">
                            <Ban className="mr-1 h-3 w-3" />
                            Banned
                          </Badge>
                        ) : (
                          <Badge className="bg-emerald-500/20 text-emerald-400">
                            <UserCheck className="mr-1 h-3 w-3" />
                            Active
                          </Badge>
                        )}
                        {user.isPremium && (
                          <Badge className="bg-amber-500/20 text-amber-400">
                            <Crown className="mr-1 h-3 w-3" />
                            Premium
                          </Badge>
                        )}
                      </div>
                    </TableCell>
                    <TableCell className="text-slate-400">{formatRelativeTime(user.createdAt)}</TableCell>
                    <TableCell>
                      <DropdownMenu>
                        <DropdownMenuTrigger>
                          <Button variant="ghost" size="icon" className="h-8 w-8 text-slate-400 hover:text-white">
                            <MoreHorizontal className="h-4 w-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end" className="bg-slate-800 border-slate-700 text-white">
                          <DropdownMenuItem className="hover:bg-slate-700">
                            <Mail className="mr-2 h-4 w-4" />
                            Send Message
                          </DropdownMenuItem>
                          <DropdownMenuSeparator className="bg-slate-700" />
                          {user.isBanned ? (
                            <DropdownMenuItem className="text-emerald-400 hover:bg-emerald-500/10">
                              <UserCheck className="mr-2 h-4 w-4" />
                              Unban User
                            </DropdownMenuItem>
                          ) : (
                            <DropdownMenuItem className="text-red-400 hover:bg-red-500/10">
                              <Ban className="mr-2 h-4 w-4" />
                              Ban User
                            </DropdownMenuItem>
                          )}
                          <DropdownMenuItem className="text-red-400 hover:bg-red-500/10">
                            <Trash2 className="mr-2 h-4 w-4" />
                            Delete
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
