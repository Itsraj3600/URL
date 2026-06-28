interface StatCardProps {
  title: string
  value: string
  icon: string
  trend?: string
  status?: 'success' | 'warning' | 'danger' | 'info'
}

export default function StatCard({ title, value, icon, trend, status }: StatCardProps) {
  const statusColors = {
    success: 'bg-green-500/20 text-green-400 border-green-500/30',
    warning: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
    danger: 'bg-red-500/20 text-red-400 border-red-500/30',
    info: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
  }

  return (
    <div
      className={`bg-zinc-900 border border-zinc-800 rounded-xl p-4 ${
        status ? statusColors[status] : ''
      }`}
    >
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm text-zinc-400">{title}</p>
          <p className="text-2xl font-bold mt-1">{value}</p>
          {trend && (
            <p className="text-xs text-zinc-500 mt-1">{trend}</p>
          )}
        </div>
        <span className="text-2xl">{icon}</span>
      </div>
    </div>
  )
}
