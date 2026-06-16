import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { api } from '../api/client'
import type { ExplorerResponse } from '../types/api'
import ChunkViewer from '../components/ChunkViewer'

const STRATEGY_LABELS: Record<string, string> = {
  fixed: 'Fixed Size',
  sentence_window: 'Sentence Window',
  hierarchical: 'Hierarchical',
}

const STRATEGY_COLORS: Record<string, string> = {
  fixed: 'border-mgray',
  sentence_window: 'border-teal2',
  hierarchical: 'border-teal',
}

export default function Explorer() {
  const { corpusId } = useParams<{ corpusId: string }>()
  const navigate = useNavigate()
  const [question, setQuestion] = useState('')
  const [compressionEnabled, setCompressionEnabled] = useState(false)
  const [result, setResult] = useState<ExplorerResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function handleQuery(e: React.FormEvent) {
    e.preventDefault()
    if (!question.trim() || !corpusId) return
    setError(null)
    setLoading(true)
    try {
      const data = await api.explorer({
        corpus_id: corpusId,
        question: question.trim(),
        compression_enabled: compressionEnabled,
      })
      setResult(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Query failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-bg p-8">
      <div className="max-w-6xl mx-auto flex flex-col gap-6">
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-lgray text-2xl font-bold">Strategy Explorer</h1>
            <p className="text-mgray text-xs font-mono mt-1">{corpusId}</p>
          </div>
          <button
            onClick={() => navigate(`/comparison/${corpusId}`)}
            className="px-4 py-2 rounded-lg border border-border text-lgray text-sm hover:border-teal transition-colors"
          >
            ← Comparison
          </button>
        </div>

        {/* Query form */}
        <form onSubmit={handleQuery} className="bg-card border border-border rounded-xl p-6 flex flex-col gap-4">
          <div className="flex gap-3">
            <input
              type="text"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="Ask a question about your corpus…"
              className="flex-1 bg-card2 border border-border rounded-lg px-4 py-2 text-lgray text-sm focus:outline-none focus:border-teal placeholder:text-mgray"
            />
            <button
              type="submit"
              disabled={loading || !question.trim()}
              className="bg-teal text-bg font-semibold px-6 py-2 rounded-lg hover:bg-teal2 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Querying…' : 'Query'}
            </button>
          </div>
          <label className="flex items-center gap-2 cursor-pointer w-fit">
            <input
              type="checkbox"
              checked={compressionEnabled}
              onChange={(e) => setCompressionEnabled(e.target.checked)}
              className="accent-teal w-4 h-4"
            />
            <span className="text-lgray text-sm">Enable ScaleDown compression</span>
          </label>
        </form>

        {error && <p className="text-amber text-sm">{error}</p>}

        {result && (
          <>
            <p className="text-mgray text-sm">
              Question: <span className="text-lgray font-medium">"{result.question}"</span>
            </p>

            {/* 3-column answer layout (Screen 5) */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {result.results.map((r) => (
                <div
                  key={r.strategy}
                  className={`bg-card border-t-2 ${STRATEGY_COLORS[r.strategy]} rounded-xl p-5 flex flex-col gap-4`}
                >
                  <div className="flex items-center justify-between">
                    <h2 className="text-lgray font-semibold text-sm">{STRATEGY_LABELS[r.strategy]}</h2>
                    <span className="text-mgray text-xs font-mono">{r.latency_ms.toFixed(0)}ms</span>
                  </div>

                  <div className="bg-card2 rounded-lg p-3">
                    <p className="text-mgray text-xs uppercase tracking-widest mb-1">Answer</p>
                    <p className="text-lgray text-sm leading-relaxed">{r.answer}</p>
                  </div>

                  <div className="flex gap-3 text-xs font-mono">
                    <div className="flex-1 bg-card2 rounded p-2">
                      <span className="text-mgray block">Tokens raw</span>
                      <span className="text-lgray">{r.tokens_raw}</span>
                    </div>
                    {r.tokens_compressed !== null && (
                      <div className="flex-1 bg-card2 rounded p-2">
                        <span className="text-mgray block">Compressed</span>
                        <span className="text-teal">{r.tokens_compressed}</span>
                      </div>
                    )}
                  </div>

                  <ChunkViewer chunks={r.chunks} title="Retrieved Chunks" />
                </div>
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  )
}
