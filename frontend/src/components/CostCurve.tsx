import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
  Legend,
} from 'recharts'
import type { StrategyMetrics } from '../types/api'

const STRATEGY_COLORS: Record<string, string> = {
  fixed: '#808080',
  sentence_window: '#00B8A0',
  hierarchical: '#00E5C4',
}

interface CostCurveProps {
  strategies: StrategyMetrics[]
  compressionRatio: number
}

export default function CostCurve({ strategies, compressionRatio }: CostCurveProps) {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <ScatterChart margin={{ top: 16, right: 24, bottom: 16, left: 8 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#2E2E2E" />
        <XAxis
          dataKey="cost_inr"
          name="Cost (₹)"
          tick={{ fill: '#808080', fontSize: 11 }}
          label={{ value: 'Cost (₹)', fill: '#808080', position: 'insideBottom', offset: -4 }}
        />
        <YAxis
          dataKey="answer_relevancy"
          name="Relevancy"
          domain={[0, 1]}
          tick={{ fill: '#808080', fontSize: 11 }}
          label={{ value: 'Relevancy', fill: '#808080', angle: -90, position: 'insideLeft' }}
        />
        <ReferenceLine y={0.80} stroke="#F5A623" strokeDasharray="6 3" label={{ value: 'target', fill: '#F5A623', fontSize: 11 }} />
        <Tooltip
          contentStyle={{ backgroundColor: '#161616', border: '1px solid #2E2E2E', borderRadius: 8 }}
          labelStyle={{ color: '#D0D0D0' }}
          itemStyle={{ color: '#D0D0D0' }}
        />
        <Legend wrapperStyle={{ color: '#D0D0D0', fontSize: 12 }} />
        {strategies.map((s) => (
          <Scatter
            key={s.strategy}
            name={s.strategy.replace('_', ' ')}
            data={[{ cost_inr: s.cost_inr * compressionRatio, answer_relevancy: s.answer_relevancy }]}
            fill={STRATEGY_COLORS[s.strategy]}
          />
        ))}
      </ScatterChart>
    </ResponsiveContainer>
  )
}
