interface CardProps {
  title?: string
  icon?: string
  children: React.ReactNode
  className?: string
}

export default function Card({ title, icon, children, className = '' }: CardProps) {
  return (
    <div
      className={`bg-zinc-900 border border-zinc-800 rounded-xl p-4 ${className}`}
    >
      {title && (
        <div className="flex items-center gap-2 mb-4 pb-3 border-b border-zinc-800">
          {icon && <span className="text-lg">{icon}</span>}
          <h3 className="font-semibold text-zinc-200">{title}</h3>
        </div>
      )}
      {children}
    </div>
  )
}
