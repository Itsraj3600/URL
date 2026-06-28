interface ProgressBarProps {
  value: number
  max?: number
  label?: string
  showPercentage?: boolean
}

export default function ProgressBar({
  value,
  max = 100,
  label,
  showPercentage = true,
}: ProgressBarProps) {
  const percentage = Math.min((value / max) * 100, 100)

  return (
    <div className="space-y-1">
      {(label || showPercentage) && (
        <div className="flex justify-between text-sm">
          <span className="text-zinc-400">{label}</span>
          {showPercentage && (
            <span className="text-zinc-300">{percentage.toFixed(1)}%</span>
          )}
        </div>
      )}
      <div className="w-full h-2 bg-zinc-800 rounded-full overflow-hidden">
        <div
          className="h-full bg-blue-500 rounded-full transition-all duration-300"
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  )
}
