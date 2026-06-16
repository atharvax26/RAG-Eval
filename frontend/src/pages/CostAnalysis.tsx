import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { api } from '../api/client'
import type { ResultsResponse } from '../types/api'
import CostCurve from '../components/CostCurve'
import MetricCard from '../components/MetricCard'

export default function CostAnalysis() {
  const { corpusId } = useParams<{ corpusId: string }>()
  const navigate = useNavigate()
  const [results, setResults] = useState<ResultsResponse | null>(null)
  const [compressionRatio, setCompressionRatio] = useState(1.0)
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
        <p className="text-mgray animate-pulse">Loading…</p>
      </div>
    )
  }

  const savings = ((1 - compressionRatio) * 100).toFixed(0)

  return (
    <div className="min-h-screen bg-bg p-8">
      <div className="max-w-4xl mx-auto flex flex-col gap-6">
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-lgray text-2xl font-bold">Cost Analysis</h1>
            <p className="text-mgray text-xs font-mono mt-1">{corpusId}</p>
          </div>
          <button
            onClick={() => navigate(`/comparison/${corpusId}`)}
            className="px-4 py-2 rounded-lg border border-border text-lgray text-sm hover:border-teal transition-colors"
          >
            ← Comparison
          </button>
        </div>

        {/* Compression slider */}
        <div className="bg-card border border-border rounded-xl p-6 flex flex-col gap-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lgray font-semibold">ScaleDown Compression Ratio</h2>
            <span className="text-teal font-mono font-bold">{compressionRatio.toFixed(2)}×</span>
          </div>
          <input
            type="range"
            min={0.3}
            max={1.0}
            step={0.01}
            value={compressionRatio}
            onChange={(e) => setCompressionRatio(Number(e.target.value))}
            className="w-full accent-teal"
          />
          <div className="flex justify-between text-mgray text-xs">
            <span>0.30× (aggressive)</span>
            <span className="text-teal">{savings}% token savings</span>
            <span>1.00× (none)</span>
          </div>
        </div>

        {/* Scatter chart */}
        <div className="bg-card border border-border rounded-xl p-6">
          <h2 className="text-lgray font-semibold mb-1">Cost vs Relevancy</h2>
          <p className="text-mgray text-xs mb-4">Amber dashed line = 0.80 target. Lower cost, higher relevancy is better.</p>
          <CostCurve strategies={results.strategies} compressionRatio={compressionRatio} />
        </div>

        {/* Summary cards */}
        <div className="grid grid-cols-3 gap-3">
          {results.strategies.map((s) => (
            <MetricCard
              key={s.strategy}
              label={s.strategy.replace('_', ' ')}
              value={`₹${(s.cost_inr * compressionRatio).toFixed(4)}`}
            />
          ))}
        </div>
      </div>
    </div>
  )
}
