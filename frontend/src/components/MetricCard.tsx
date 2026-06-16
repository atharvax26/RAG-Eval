interface MetricCardProps {
  label: string
  value: number | string
  unit?: string
  highlight?: boolean
}

export default function MetricCard({ label, value, unit, highlight }: MetricCardProps) {
  const display = typeof value === 'number' ? value.toFixed(3) : value
  return (
    <div className="bg-card2 rounded-lg p-4 border border-border flex flex-col gap-1">
      <span className="text-mgray text-xs uppercase tracking-widest">{label}</span>
      <span className={`text-2xl font-mono font-bold ${highlight ? 'text-teal' : 'text-lgray'}`}>
        {display}
        {unit && <span className="text-sm text-mgray ml-1">{unit}</span>}
      </span>
    </div>
  )
}
