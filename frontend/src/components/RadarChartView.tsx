import {
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  Radar,
  Legend,
  ResponsiveContainer,
  Tooltip,
} from 'recharts'
import type { StrategyMetrics } from '../types/api'

const STRATEGY_COLORS: Record<string, string> = {
  fixed: '#808080',
  sentence_window: '#00B8A0',
  hierarchical: '#00E5C4',
}

const METRIC_KEYS = [
  { key: 'context_precision', label: 'Precision' },
  { key: 'context_recall', label: 'Recall' },
  { key: 'faithfulness', label: 'Faithfulness' },
  { key: 'answer_relevancy', label: 'Relevancy' },
]

interface RadarChartViewProps {
  strategies: StrategyMetrics[]
}

export default function RadarChartView({ strategies }: RadarChartViewProps) {
  const data = METRIC_KEYS.map(({ key, label }) => {
    const entry: Record<string, string | number> = { metric: label }
    strategies.forEach((s) => {
      entry[s.strategy] = Number((s[key as keyof StrategyMetrics] as number).toFixed(3))
    })
    return entry
  })

  return (
    <ResponsiveContainer width="100%" height={320}>
      <RadarChart data={data} margin={{ top: 16, right: 24, bottom: 16, left: 24 }}>
        <PolarGrid stroke="#2E2E2E" />
        <PolarAngleAxis dataKey="metric" tick={{ fill: '#D0D0D0', fontSize: 12 }} />
        {strategies.map((s) => (
          <Radar
            key={s.strategy}
            name={s.strategy.replace('_', ' ')}
            dataKey={s.strategy}
            stroke={STRATEGY_COLORS[s.strategy]}
            fill={STRATEGY_COLORS[s.strategy]}
            fillOpacity={0.15}
          />
        ))}
        <Legend
          wrapperStyle={{ color: '#D0D0D0', fontSize: 12 }}
        />
        <Tooltip
          contentStyle={{ backgroundColor: '#161616', border: '1px solid #2E2E2E', borderRadius: 8 }}
          labelStyle={{ color: '#D0D0D0' }}
          itemStyle={{ color: '#D0D0D0' }}
        />
      </RadarChart>
    </ResponsiveContainer>
  )
}
