import type {
  IngestRequest,
  IngestResponse,
  IngestStatusResponse,
  EvaluateRequest,
  EvaluateResponse,
  EvalStatusResponse,
  ResultsResponse,
  RunListItem,
  ExplorerRequest,
  ExplorerResponse,
} from '../types/api'

const BASE = '/api'

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...init?.headers },
    ...init,
  })
  if (!res.ok) {
    const text = await res.text()
    throw new Error(`${res.status}: ${text}`)
  }
  return res.json() as Promise<T>
}

export const api = {
  ingest: (body: IngestRequest) =>
    request<IngestResponse>('/ingest', { method: 'POST', body: JSON.stringify(body) }),

  ingestStatus: (corpusId: string) =>
    request<IngestStatusResponse>(`/ingest/${corpusId}/status`),

  evaluate: (body: EvaluateRequest) =>
    request<EvaluateResponse>('/evaluate', { method: 'POST', body: JSON.stringify(body) }),

  evalStatus: (runId: string) =>
    request<EvalStatusResponse>(`/evaluate/${runId}/status`),

  results: (corpusId: string, strategies?: string[]) => {
    const qs = strategies?.length ? `?strategies=${strategies.join(',')}` : ''
    return request<ResultsResponse>(`/results/${corpusId}${qs}`)
  },

  runs: (params?: { corpus_id?: string; limit?: number; offset?: number }) => {
    const qs = new URLSearchParams(
      Object.entries(params ?? {}).filter(([, v]) => v !== undefined).map(([k, v]) => [k, String(v)])
    ).toString()
    return request<RunListItem[]>(`/runs${qs ? `?${qs}` : ''}`)
  },

  explorer: (body: ExplorerRequest) =>
    request<ExplorerResponse>('/explorer', { method: 'POST', body: JSON.stringify(body) }),

  health: () => request<{ status: string }>('/health'),
}
