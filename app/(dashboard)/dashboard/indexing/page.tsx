'use client'

import { useState } from 'react'
import Card from '@/app/(dashboard)/components/Card'
import ProgressBar from '@/app/(dashboard)/components/ProgressBar'

const mockJobs = [
  {
    id: 'job1',
    channel_name: 'Movies HD',
    channel_id: -1001234567890,
    status: 'running',
    progress: 74,
    processed: 45218,
    inserted: 44892,
    duplicates: 326,
    errors: 0,
    speed: 145,
    eta: '11m'
  },
  {
    id: 'job2',
    channel_name: 'TV Shows',
    channel_id: -1009876543210,
    status: 'paused',
    progress: 45,
    processed: 28500,
    inserted: 28100,
    duplicates: 400,
    errors: 0,
    speed: 0,
    eta: 'N/A'
  },
  {
    id: 'job3',
    channel_name: 'Anime Collection',
    channel_id: -1001112223334,
    status: 'pending',
    progress: 0,
    processed: 0,
    inserted: 0,
    duplicates: 0,
    errors: 0,
    speed: 0,
    eta: 'Waiting',
    position: 2
  }
]

export default function IndexingPage() {
  const [selectedJob, setSelectedJob] = useState<string | null>(null)

  const statusColors = {
    running: 'bg-blue-500/20 text-blue-400',
    paused: 'bg-yellow-500/20 text-yellow-400',
    pending: 'bg-zinc-700 text-zinc-400',
    completed: 'bg-green-500/20 text-green-400',
    failed: 'bg-red-500/20 text-red-400',
    cancelled: 'bg-zinc-700 text-zinc-500',
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Index Manager</h1>
          <p className="text-zinc-400">Manage indexing jobs</p>
        </div>
        <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
          + New Job
        </button>
      </div>

      {/* Active Jobs */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {mockJobs.map((job) => (
          <Card key={job.id} className={selectedJob === job.id ? 'ring-2 ring-blue-500' : ''}>
            <div className="space-y-4">
              {/* Job Header */}
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="font-semibold">{job.channel_name}</h3>
                  <p className="text-sm text-zinc-500">ID: {job.channel_id}</p>
                </div>
                <span className={`px-2 py-1 rounded text-sm ${statusColors[job.status as keyof typeof statusColors]}`}>
                  {job.status.charAt(0).toUpperCase() + job.status.slice(1)}
                </span>
              </div>

              {/* Progress */}
              {job.status === 'running' && (
                <ProgressBar value={job.progress} />
              )}

              {/* Stats */}
              <div className="grid grid-cols-4 gap-4 text-sm">
                <div>
                  <p className="text-zinc-500">Processed</p>
                  <p className="font-mono">{job.processed.toLocaleString()}</p>
                </div>
                <div>
                  <p className="text-zinc-500">Inserted</p>
                  <p className="font-mono">{job.inserted.toLocaleString()}</p>
                </div>
                <div>
                  <p className="text-zinc-500">Duplicates</p>
                  <p className="font-mono">{job.duplicates.toLocaleString()}</p>
                </div>
                <div>
                  <p className="text-zinc-500">Errors</p>
                  <p className="font-mono text-red-400">{job.errors}</p>
                </div>
              </div>

              {/* Speed & ETA */}
              {job.status === 'running' && (
                <div className="flex items-center justify-between text-sm pt-2 border-t border-zinc-800">
                  <div className="flex items-center gap-4">
                    <span className="text-zinc-400">Speed: <span className="text-zinc-200">{job.speed} f/s</span></span>
                    <span className="text-zinc-400">ETA: <span className="text-zinc-200">{job.eta}</span></span>
                  </div>
                </div>
              )}

              {/* Queue Position */}
              {job.status === 'pending' && 'position' in job && (
                <div className="text-sm text-zinc-400 pt-2 border-t border-zinc-800">
                  Queue Position: #{job.position}
                </div>
              )}

              {/* Actions */}
              <div className="flex items-center gap-2 pt-2 border-t border-zinc-800">
                {job.status === 'running' && (
                  <>
                    <button className="px-3 py-1 bg-yellow-600/20 text-yellow-400 rounded text-sm hover:bg-yellow-600/30">
                      Pause
                    </button>
                    <button className="px-3 py-1 bg-red-600/20 text-red-400 rounded text-sm hover:bg-red-600/30">
                      Cancel
                    </button>
                  </>
                )}
                {job.status === 'paused' && (
                  <>
                    <button className="px-3 py-1 bg-green-600/20 text-green-400 rounded text-sm hover:bg-green-600/30">
                      Resume
                    </button>
                    <button className="px-3 py-1 bg-red-600/20 text-red-400 rounded text-sm hover:bg-red-600/30">
                      Cancel
                    </button>
                  </>
                )}
                {job.status === 'pending' && (
                  <>
                    <button className="px-3 py-1 bg-blue-600/20 text-blue-400 rounded text-sm hover:bg-blue-600/30">
                      Start Now
                    </button>
                    <button className="px-3 py-1 bg-red-600/20 text-red-400 rounded text-sm hover:bg-red-600/30">
                      Remove
                    </button>
                  </>
                )}
              </div>
            </div>
          </Card>
        ))}
      </div>

      {/* Start New Index */}
      <Card title="Start New Index Job" icon="➕">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm text-zinc-400 mb-1">Channel ID</label>
            <input
              type="text"
              placeholder="-1001234567890"
              className="w-full px-4 py-2 bg-zinc-800 border border-zinc-700 rounded-lg text-sm focus:outline-none focus:border-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm text-zinc-400 mb-1">Last Message ID</label>
            <input
              type="number"
              placeholder="50000"
              className="w-full px-4 py-2 bg-zinc-800 border border-zinc-700 rounded-lg text-sm focus:outline-none focus:border-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm text-zinc-400 mb-1">Priority</label>
            <select className="w-full px-4 py-2 bg-zinc-800 border border-zinc-700 rounded-lg text-sm focus:outline-none focus:border-blue-500">
              <option>Normal</option>
              <option>High</option>
              <option>Low</option>
            </select>
          </div>
        </div>
        <button className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
          Add to Queue
        </button>
      </Card>
    </div>
  )
}
