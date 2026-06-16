import { useEffect, useState, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { api } from '../api/client'
import type { IngestStatusResponse } from '../types/api'

const STATUS_LABEL: Record<string, string> = {
  pending: 'Pending',
  indexing: 'Indexing…',
  ready: 'Ready',
  error: 'Error',
}

const STATUS_COLOR: Record<string, string> = {
  pending: 'text-mgray',
  indexing: 'text-amber',
  ready: 'text-teal',
  error: 'text-amber',
}

const STRATEGY_LABELS: Record<string, string> = {
  fixed: 'Fixed Size',
  sentence_window: 'Sentence Window',
  hierarchical: 'Hierarchical',
}

export default function Progress() {
  const { corpusId } = useParams<{ corpusId: string }>()
  const navigate = useNavigate()
  const [status, setStatus] = useState<IngestStatusResponse | null>(null)
  const [error, setError] = useState<string | null>(null)
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null)

  useEffect(() => {
    if (!corpusId) return

    async function poll() {
      try {
        const data = await api.ingestStatus(corpusId!)
        setStatus(data)
        const statuses = Object.values(data.strategy_statuses)
        const allReady = statuses.length > 0 && statuses.every((s) => s === 'ready')
        if (allReady) {
          clearInterval(intervalRef.current!)
          intervalRef.current = null
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch status')
      }
    }

    poll()
    intervalRef.current = setInterval(poll, 1500)

    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current)
    }
  }, [corpusId])

  const statuses = status?.strategy_statuses ?? {}
  const allReady = Object.values(statuses).length > 0 && Object.values(statuses).every((s) => s === 'ready')

  return (
    <div className="min-h-screen bg-bg flex items-center justify-center p-8">
      <div className="w-full max-w-md bg-card rounded-2xl border border-border p-8 flex flex-col gap-6">
        <div>
          <h1 className="text-lgray text-xl font-bold">Indexing Progress</h1>
          <p className="text-mgray text-xs font-mono mt-1">{corpusId}</p>
        </div>

        {error && <p className="text-amber text-sm">{error}</p>}

        <div className="flex flex-col gap-3">
          {Object.entries(statuses).map(([strategy, st]) => (
            <div key={strategy} className="bg-card2 border border-border rounded-lg p-4 flex items-center justify-between">
              <span className="text-lgray text-sm">{STRATEGY_LABELS[strategy] ?? strategy}</span>
              <div className="flex items-center gap-2">
                {st === 'indexing' && (
                  <span className="w-3 h-3 rounded-full bg-amber animate-pulse" />
                )}
                {st === 'ready' && (
                  <span className="w-3 h-3 rounded-full bg-teal" />
                )}
                {st === 'pending' && (
                  <span className="w-3 h-3 rounded-full bg-border" />
                )}
                <span className={`text-sm font-mono ${STATUS_COLOR[st] ?? 'text-mgray'}`}>
                  {STATUS_LABEL[st] ?? st}
                </span>
              </div>
            </div>
          ))}

          {!status && !error && (
            <div className="text-mgray text-sm text-center animate-pulse">Connecting…</div>
          )}
        </div>

        <button
          disabled={!allReady}
          onClick={() => navigate(`/comparison/${corpusId}`)}
          className="bg-teal text-bg font-semibold rounded-lg py-3 hover:bg-teal2 transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
        >
          {allReady ? 'View Comparison →' : 'Waiting for all strategies…'}
        </button>
      </div>
    </div>
  )
}
