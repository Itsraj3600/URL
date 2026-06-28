'use client'

import { useState } from 'react'
import Card from '@/app/(dashboard)/components/Card'

export default function SettingsPage() {
  const [settings, setSettings] = useState({
    batch_size: 500,
    cache_ttl: 600,
    max_results: 10,
    worker_count: 8,
    log_level: 'INFO',
    feature_auto_index: true,
    feature_spell_check: true,
    feature_imdb: true,
    feature_url_shortener: false,
    floodwait_delay: 30,
  })

  const handleChange = (key: string, value: any) => {
    setSettings(prev => ({ ...prev, [key]: value }))
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Settings</h1>
          <p className="text-zinc-400">Configure bot behavior</p>
        </div>
        <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
          Save Changes
        </button>
      </div>

      {/* Indexing Settings */}
      <Card title="Indexing Settings" icon="📁">
        <div className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm text-zinc-400 mb-1">Batch Size</label>
              <input
                type="number"
                value={settings.batch_size}
                onChange={(e) => handleChange('batch_size', parseInt(e.target.value))}
                className="w-full px-4 py-2 bg-zinc-800 border border-zinc-700 rounded-lg focus:outline-none focus:border-blue-500"
              />
              <p className="text-xs text-zinc-500 mt-1">Messages per bulk write</p>
            </div>
            <div>
              <label className="block text-sm text-zinc-400 mb-1">Worker Count</label>
              <input
                type="number"
                value={settings.worker_count}
                onChange={(e) => handleChange('worker_count', parseInt(e.target.value))}
                className="w-full px-4 py-2 bg-zinc-800 border border-zinc-700 rounded-lg focus:outline-none focus:border-blue-500"
              />
            </div>
          </div>
          <div>
            <label className="block text-sm text-zinc-400 mb-1">FloodWait Delay (seconds)</label>
            <input
              type="number"
              value={settings.floodwait_delay}
              onChange={(e) => handleChange('floodwait_delay', parseInt(e.target.value))}
              className="w-full px-4 py-2 bg-zinc-800 border border-zinc-700 rounded-lg focus:outline-none focus:border-blue-500"
            />
          </div>
        </div>
      </Card>

      {/* Search Settings */}
      <Card title="Search Settings" icon="🔍">
        <div className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm text-zinc-400 mb-1">Cache TTL (seconds)</label>
              <input
                type="number"
                value={settings.cache_ttl}
                onChange={(e) => handleChange('cache_ttl', parseInt(e.target.value))}
                className="w-full px-4 py-2 bg-zinc-800 border border-zinc-700 rounded-lg focus:outline-none focus:border-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm text-zinc-400 mb-1">Max Results Per Page</label>
              <input
                type="number"
                value={settings.max_results}
                onChange={(e) => handleChange('max_results', parseInt(e.target.value))}
                className="w-full px-4 py-2 bg-zinc-800 border border-zinc-700 rounded-lg focus:outline-none focus:border-blue-500"
              />
            </div>
          </div>
        </div>
      </Card>

      {/* Feature Flags */}
      <Card title="Feature Flags" icon="🚩">
        <div className="space-y-4">
          {[
            { key: 'feature_auto_index', label: 'Auto Index', desc: 'Automatically index new files in watched channels' },
            { key: 'feature_spell_check', label: 'Spell Check', desc: 'Suggest corrections for misspelled queries' },
            { key: 'feature_imdb', label: 'IMDB Integration', desc: 'Fetch movie metadata from IMDB' },
            { key: 'feature_url_shortener', label: 'URL Shortener', desc: 'Use short links for non-premium users' },
          ].map((feature) => (
            <div key={feature.key} className="flex items-center justify-between p-3 bg-zinc-800/50 rounded-lg">
              <div>
                <p className="font-medium">{feature.label}</p>
                <p className="text-sm text-zinc-500">{feature.desc}</p>
              </div>
              <button
                onClick={() => handleChange(feature.key, !settings[feature.key as keyof typeof settings])}
                className={`w-12 h-6 rounded-full transition-colors ${
                  settings[feature.key as keyof typeof settings] ? 'bg-blue-600' : 'bg-zinc-700'
                }`}
              >
                <div
                  className={`w-5 h-5 bg-white rounded-full transition-transform ${
                    settings[feature.key as keyof typeof settings] ? 'translate-x-6' : 'translate-x-0.5'
                  }`}
                />
              </button>
            </div>
          ))}
        </div>
      </Card>

      {/* Logging */}
      <Card title="Logging" icon="📝">
        <div className="space-y-4">
          <div>
            <label className="block text-sm text-zinc-400 mb-1">Log Level</label>
            <select
              value={settings.log_level}
              onChange={(e) => handleChange('log_level', e.target.value)}
              className="w-full px-4 py-2 bg-zinc-800 border border-zinc-700 rounded-lg focus:outline-none focus:border-blue-500"
            >
              <option value="DEBUG">DEBUG</option>
              <option value="INFO">INFO</option>
              <option value="WARNING">WARNING</option>
              <option value="ERROR">ERROR</option>
            </select>
          </div>
        </div>
      </Card>

      {/* Danger Zone */}
      <Card title="Danger Zone" icon="⚠️" className="border-red-500/50">
        <div className="space-y-4">
          <div className="flex items-center justify-between p-3 bg-red-500/10 border border-red-500/30 rounded-lg">
            <div>
              <p className="font-medium text-red-400">Clear All Cache</p>
              <p className="text-sm text-zinc-500">Remove all cached search results</p>
            </div>
            <button className="px-3 py-1 bg-red-600 text-white rounded text-sm hover:bg-red-700">
              Clear
            </button>
          </div>
          <div className="flex items-center justify-between p-3 bg-red-500/10 border border-red-500/30 rounded-lg">
            <div>
              <p className="font-medium text-red-400">Reset Statistics</p>
              <p className="text-sm text-zinc-500">Clear all recorded statistics</p>
            </div>
            <button className="px-3 py-1 bg-red-600 text-white rounded text-sm hover:bg-red-700">
              Reset
            </button>
          </div>
        </div>
      </Card>
    </div>
  )
}
