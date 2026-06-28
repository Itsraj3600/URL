'use client';

import { useState } from 'react';
import { Save } from 'lucide-react';

export default function SettingsPage() {
  const [settings, setSettings] = useState({
    workerCount: 3,
    batchSize: 100,
    searchTimeout: 30,
    cacheTTL: 3600,
    autoIndex: true,
    loggingLevel: 'info',
  });

  const [saved, setSaved] = useState(false);

  const handleSave = () => {
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  const inputClass = 'bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-white w-full focus:outline-none focus:border-blue-500';
  const labelClass = 'block text-sm font-medium text-slate-300 mb-2';

  return (
    <div className="space-y-6 p-8">
      <div>
        <h1 className="text-3xl font-bold text-white">Settings</h1>
        <p className="text-slate-400 mt-1">Configure bot behavior and performance</p>
      </div>

      <div className="max-w-2xl space-y-6">
        {/* Worker Configuration */}
        <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-6">
          <h2 className="text-lg font-semibold text-white mb-4">Worker Configuration</h2>
          
          <div className="space-y-4">
            <div>
              <label className={labelClass}>Number of Workers</label>
              <input
                type="number"
                min="1"
                max="10"
                value={settings.workerCount}
                onChange={(e) => setSettings({ ...settings, workerCount: parseInt(e.target.value) })}
                className={inputClass}
              />
              <p className="text-xs text-slate-400 mt-1">Restart required to apply changes</p>
            </div>

            <div>
              <label className={labelClass}>Batch Size</label>
              <input
                type="number"
                value={settings.batchSize}
                onChange={(e) => setSettings({ ...settings, batchSize: parseInt(e.target.value) })}
                className={inputClass}
              />
              <p className="text-xs text-slate-400 mt-1">Items processed per batch</p>
            </div>
          </div>
        </div>

        {/* Search Configuration */}
        <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-6">
          <h2 className="text-lg font-semibold text-white mb-4">Search Configuration</h2>
          
          <div>
            <label className={labelClass}>Search Timeout (seconds)</label>
            <input
              type="number"
              value={settings.searchTimeout}
              onChange={(e) => setSettings({ ...settings, searchTimeout: parseInt(e.target.value) })}
              className={inputClass}
            />
          </div>
        </div>

        {/* Cache Configuration */}
        <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-6">
          <h2 className="text-lg font-semibold text-white mb-4">Cache Configuration</h2>
          
          <div>
            <label className={labelClass}>Cache TTL (seconds)</label>
            <input
              type="number"
              value={settings.cacheTTL}
              onChange={(e) => setSettings({ ...settings, cacheTTL: parseInt(e.target.value) })}
              className={inputClass}
            />
          </div>
        </div>

        {/* Feature Flags */}
        <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-6">
          <h2 className="text-lg font-semibold text-white mb-4">Feature Flags</h2>
          
          <label className="flex items-center gap-3 cursor-pointer">
            <input
              type="checkbox"
              checked={settings.autoIndex}
              onChange={(e) => setSettings({ ...settings, autoIndex: e.target.checked })}
              className="w-4 h-4"
            />
            <span className="text-slate-300">Enable Automatic Indexing</span>
          </label>
        </div>

        {/* Logging */}
        <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-6">
          <h2 className="text-lg font-semibold text-white mb-4">Logging</h2>
          
          <div>
            <label className={labelClass}>Logging Level</label>
            <select
              value={settings.loggingLevel}
              onChange={(e) => setSettings({ ...settings, loggingLevel: e.target.value })}
              className={inputClass}
            >
              <option>debug</option>
              <option>info</option>
              <option>warning</option>
              <option>error</option>
            </select>
          </div>
        </div>

        {/* Save Button */}
        <div className="flex items-center gap-3">
          <button
            onClick={handleSave}
            className="flex items-center gap-2 px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors font-medium"
          >
            <Save className="w-4 h-4" />
            Save Settings
          </button>
          {saved && <p className="text-sm text-green-400">Settings saved!</p>}
        </div>
      </div>
    </div>
  );
}
