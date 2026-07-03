'use client'

import { Bell, Search, Moon, Sun, User } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { Badge } from '@/components/ui/badge'
import { useState } from 'react'

export function TopNav() {
  const [isDark, setIsDark] = useState(true)

  return (
    <header className="sticky top-0 z-30 flex h-16 items-center gap-4 border-b border-slate-700/50 bg-slate-900/80 backdrop-blur-xl px-4 lg:px-6">
      {/* Search */}
      <div className="relative flex-1 max-w-md ml-12 lg:ml-0">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
        <Input
          placeholder="Search files, users, channels..."
          className="pl-10 bg-slate-800/50 border-slate-700 text-white placeholder:text-slate-500 focus:border-cyan-500/50"
        />
      </div>

      <div className="flex items-center gap-2 ml-auto">
        {/* Notifications */}
        <DropdownMenu>
          <DropdownMenuTrigger>
            <Button variant="ghost" size="icon" className="relative text-slate-400 hover:text-white hover:bg-slate-800/50">
              <Bell className="h-5 w-5" />
              <Badge className="absolute -top-1 -right-1 h-5 w-5 rounded-full p-0 flex items-center justify-center bg-cyan-500 text-[10px] font-bold text-white border-2 border-slate-900">
                3
              </Badge>
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-80 bg-slate-800 border-slate-700 text-white">
            <DropdownMenuLabel className="text-slate-300 font-normal">
              <div className="flex items-center justify-between">
                <span>Notifications</span>
                <Badge className="bg-cyan-500/20 text-cyan-400 hover:bg-cyan-500/30">3 new</Badge>
              </div>
            </DropdownMenuLabel>
            <DropdownMenuSeparator className="bg-slate-700" />
            <DropdownMenuItem className="flex flex-col items-start gap-1 p-3 hover:bg-slate-700/50 focus:bg-slate-700/50">
              <p className="text-sm font-medium">New user registered</p>
              <p className="text-xs text-slate-400">2 minutes ago</p>
            </DropdownMenuItem>
            <DropdownMenuItem className="flex flex-col items-start gap-1 p-3 hover:bg-slate-700/50 focus:bg-slate-700/50">
              <p className="text-sm font-medium">Indexing completed for channel</p>
              <p className="text-xs text-slate-400">15 minutes ago</p>
            </DropdownMenuItem>
            <DropdownMenuItem className="flex flex-col items-start gap-1 p-3 hover:bg-slate-700/50 focus:bg-slate-700/50">
              <p className="text-sm font-medium">Premium user expired</p>
              <p className="text-xs text-slate-400">1 hour ago</p>
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>

        {/* Theme toggle */}
        <Button
          variant="ghost"
          size="icon"
          className="text-slate-400 hover:text-white hover:bg-slate-800/50"
          onClick={() => setIsDark(!isDark)}
        >
          {isDark ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
        </Button>

        {/* User menu */}
        <DropdownMenu>
          <DropdownMenuTrigger>
            <Button variant="ghost" className="relative h-9 w-9 rounded-full">
              <Avatar className="h-9 w-9 border-2 border-cyan-500/50">
                <AvatarImage src="/avatar.png" alt="Admin" />
                <AvatarFallback className="bg-gradient-to-br from-cyan-500 to-blue-600 text-white font-bold">
                  AD
                </AvatarFallback>
              </Avatar>
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-56 bg-slate-800 border-slate-700 text-white">
            <DropdownMenuLabel className="font-normal">
              <div className="flex flex-col space-y-1">
                <p className="text-sm font-medium">Admin</p>
                <p className="text-xs text-slate-400">admin@cine3600.com</p>
              </div>
            </DropdownMenuLabel>
            <DropdownMenuSeparator className="bg-slate-700" />
            <DropdownMenuItem className="hover:bg-slate-700/50 focus:bg-slate-700/50">
              <User className="mr-2 h-4 w-4" />
              Profile
            </DropdownMenuItem>
            <DropdownMenuItem className="hover:bg-slate-700/50 focus:bg-slate-700/50">
              Settings
            </DropdownMenuItem>
            <DropdownMenuSeparator className="bg-slate-700" />
            <DropdownMenuItem className="text-red-400 hover:bg-red-500/10 focus:bg-red-500/10">
              Log out
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </header>
  )
}
