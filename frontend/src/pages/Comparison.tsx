import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { api } from '../api/client'
import type { ResultsResponse, StrategyMetrics } from '../types/api'
import RadarChartView from '../components/RadarChartView'
import MetricCard from '../components/MetricCard'

const STRATEGY_LABELS: Record<string, string> = {
  fixed: 'Fixed Size',
  sentence_window: 'Sentence Window',
  hierarchical: 'Hierarchical',
}

const METRIC_KEYS: { key: keyof StrategyMetrics; label: string }[] = [
  { key: 'context_precision', label: 'Precision' },
  { key: 'context_recall', label: 'Recall' },
  { key: 'faithfulness', label: 'Faithfulness' },
  { key: 'answer_relevancy', label: 'Relevancy' },
]

export default function Comparison() {
  const { corpusId } = useParams<{ corpusId: string }>()
  const navigate = useNavigate()
  const [results, setResults] = useState<ResultsResponse | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!corpusId) return
    api.results(corpusId)
      .then(setResults)
      .catch((err) => setError(err instanceof Error ? err.message : 'Failed to load results'))
  }, [corpusId])

  if (error) {
    return (
      <div className="min-h-screen bg-bg flex items-center justify-center">
        <p className="text-amber">{error}</p>
      </div>
    )
  }

  if (!results) {
    return (
      <div className="min-h-screen bg-bg flex items-center justify-center">
        <p className="text-mgray animate-pulse">Loading results…</p>
      </div>
    )
  }

  const best = results.strategies.reduce((a, b) =>
    a.answer_relevancy >= b.answer_relevancy ? a : b
  )

  return (
    <div className="min-h-screen bg-bg p-8">
      <div className="max-w-5xl mx-auto flex flex-col gap-6">
        {/* Header */}
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-lgray text-2xl font-bold">Strategy Comparison</h1>
            <p className="text-mgray text-xs font-mono mt-1">{corpusId}</p>
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => navigate(`/cost/${corpusId}`)}
              className="px-4 py-2 rounded-lg border border-border text-lgray text-sm hover:border-teal transition-colors"
            >
              Cost Analysis →
            </button>
            <button
              onClick={() => navigate(`/explorer/${corpusId}`)}
              className="px-4 py-2 rounded-lg border border-teal text-teal text-sm hover:bg-card2 transition-colors"
            >
              Explorer →
            </button>
          </div>
        </div>

        {/* Winner banner */}
        <div className="bg-card border border-teal rounded-xl p-4 flex items-center gap-3">
          <span className="text-teal text-lg">★</span>
          <div>
            <span className="text-teal font-semibold">{STRATEGY_LABELS[best.strategy]}</span>
            <span className="text-lgray text-sm ml-2">best overall relevancy ({best.answer_relevancy.toFixed(3)})</span>
          </div>
        </div>

        {/* Radar chart */}
        <div className="bg-card border border-border rounded-xl p-6">
          <h2 className="text-lgray font-semibold mb-4">RAGAS Metrics Radar</h2>
          <RadarChartView strategies={results.strategies} />
        </div>

        {/* Metrics table */}
        <div className="bg-card border border-border rounded-xl p-6 overflow-x-auto">
          <h2 className="text-lgray font-semibold mb-4">Detailed Metrics</h2>
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border">
                <th className="text-mgray text-left py-2 pr-4 font-normal uppercase text-xs tracking-widest">Strategy</th>
                {METRIC_KEYS.map(({ label }) => (
                  <th key={label} className="text-mgray text-right py-2 px-3 font-normal uppercase text-xs tracking-widest">{label}</th>
                ))}
                <th className="text-mgray text-right py-2 px-3 font-normal uppercase text-xs tracking-widest">Latency (ms)</th>
                <th className="text-mgray text-right py-2 px-3 font-normal uppercase text-xs tracking-widest">Cost (₹)</th>
              </tr>
            </thead>
            <tbody>
              {results.strategies.map((s) => (
                <tr key={s.strategy} className="border-b border-border last:border-0 hover:bg-card2 transition-colors">
                  <td className="py-3 pr-4">
                    <span className={`font-medium ${s.strategy === best.strategy ? 'text-teal' : 'text-lgray'}`}>
                      {STRATEGY_LABELS[s.strategy]}
                    </span>
                  </td>
                  {METRIC_KEYS.map(({ key }) => (
                    <td key={key} className="text-right px-3 py-3 font-mono text-lgray">
                      {(s[key] as number).toFixed(3)}
                    </td>
                  ))}
                  <td className="text-right px-3 py-3 font-mono text-lgray">{s.avg_latency_ms.toFixed(0)}</td>
                  <td className="text-right px-3 py-3 font-mono text-lgray">₹{s.cost_inr.toFixed(4)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Metric cards */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {METRIC_KEYS.map(({ key, label }) => (
            <MetricCard
              key={key}
              label={label}
              value={best[key] as number}
              highlight={key === 'answer_relevancy'}
            />
          ))}
        </div>
      </div>
    </div>
  )
}
