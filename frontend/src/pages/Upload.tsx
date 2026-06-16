import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api/client'
import type { StrategyId } from '../types/api'

const ALL_STRATEGIES: { id: StrategyId; label: string; description: string }[] = [
  { id: 'fixed', label: 'Fixed Size', description: '512 tokens, 50 overlap' },
  { id: 'sentence_window', label: 'Sentence Window', description: 'Window size 3' },
  { id: 'hierarchical', label: 'Hierarchical', description: '2048 / 512 / 128 tokens' },
]

export default function Upload() {
  const navigate = useNavigate()
  const [corpusName, setCorpusName] = useState('')
  const [sourceUrl, setSourceUrl] = useState('')
  const [sourceType, setSourceType] = useState<'pdf' | 'web' | 'text'>('pdf')
  const [strategies, setStrategies] = useState<Set<StrategyId>>(new Set(['fixed', 'sentence_window', 'hierarchical']))
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  function toggleStrategy(id: StrategyId) {
    setStrategies((prev) => {
      const next = new Set(prev)
      if (next.has(id)) next.delete(id)
      else next.add(id)
      return next
    })
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!corpusName.trim() || !sourceUrl.trim() || strategies.size === 0) {
      setError('Fill in all fields and select at least one strategy.')
      return
    }
    setError(null)
    setLoading(true)
    try {
      const res = await api.ingest({
        corpus_name: corpusName.trim(),
        source_url: sourceUrl.trim(),
        source_type: sourceType,
        strategies: [...strategies] as StrategyId[],
      })
      navigate(`/progress/${res.corpus_id}`)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to start ingestion')
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-bg flex items-center justify-center p-8">
      <div className="w-full max-w-lg bg-card rounded-2xl border border-border p-8 flex flex-col gap-6">
        <div>
          <h1 className="text-lgray text-2xl font-bold tracking-tight">RAG Eval Studio</h1>
          <p className="text-mgray text-sm mt-1">Benchmark chunking strategies with RAGAS metrics</p>
        </div>

        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <div className="flex flex-col gap-1">
            <label className="text-mgray text-xs uppercase tracking-widest">Corpus Name</label>
            <input
              type="text"
              value={corpusName}
              onChange={(e) => setCorpusName(e.target.value)}
              placeholder="e.g. NPTEL Lecture Notes"
              className="bg-card2 border border-border rounded-lg px-3 py-2 text-lgray text-sm focus:outline-none focus:border-teal placeholder:text-mgray"
            />
          </div>

          <div className="flex flex-col gap-1">
            <label className="text-mgray text-xs uppercase tracking-widest">Source URL</label>
            <input
              type="text"
              value={sourceUrl}
              onChange={(e) => setSourceUrl(e.target.value)}
              placeholder="https://example.com/document.pdf"
              className="bg-card2 border border-border rounded-lg px-3 py-2 text-lgray text-sm focus:outline-none focus:border-teal placeholder:text-mgray"
            />
          </div>

          <div className="flex flex-col gap-1">
            <label className="text-mgray text-xs uppercase tracking-widest">Source Type</label>
            <div className="flex gap-2">
              {(['pdf', 'web', 'text'] as const).map((t) => (
                <button
                  key={t}
                  type="button"
                  onClick={() => setSourceType(t)}
                  className={`px-4 py-2 rounded-lg text-sm border transition-colors ${
                    sourceType === t
                      ? 'bg-teal text-bg border-teal font-semibold'
                      : 'bg-card2 text-mgray border-border hover:border-teal'
                  }`}
                >
                  {t.toUpperCase()}
                </button>
              ))}
            </div>
          </div>

          <div className="flex flex-col gap-2">
            <label className="text-mgray text-xs uppercase tracking-widest">Chunking Strategies</label>
            <div className="flex flex-col gap-2">
              {ALL_STRATEGIES.map(({ id, label, description }) => (
                <button
                  key={id}
                  type="button"
                  onClick={() => toggleStrategy(id)}
                  className={`flex items-center justify-between px-4 py-3 rounded-lg border text-left transition-colors ${
                    strategies.has(id)
                      ? 'border-teal bg-card2'
                      : 'border-border bg-card2 opacity-60'
                  }`}
                >
                  <div>
                    <span className="text-lgray text-sm font-medium">{label}</span>
                    <span className="block text-mgray text-xs">{description}</span>
                  </div>
                  <span className={`w-4 h-4 rounded border-2 flex-shrink-0 ${strategies.has(id) ? 'border-teal bg-teal' : 'border-border'}`} />
                </button>
              ))}
            </div>
          </div>

          {error && <p className="text-amber text-sm">{error}</p>}

          <button
            type="submit"
            disabled={loading}
            className="bg-teal text-bg font-semibold rounded-lg py-3 mt-2 hover:bg-teal2 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Starting ingestion…' : 'Start Ingestion →'}
          </button>
        </form>
      </div>
    </div>
  )
}
