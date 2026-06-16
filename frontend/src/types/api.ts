export type StrategyId = 'fixed' | 'sentence_window' | 'hierarchical'

export interface IngestRequest {
  corpus_name: string
  source_url: string
  source_type: 'pdf' | 'web' | 'text'
  strategies: StrategyId[]
}

export interface IngestResponse {
  corpus_id: string
  message: string
}

export interface IngestStatusResponse {
  corpus_id: string
  strategy_statuses: Record<StrategyId, 'pending' | 'indexing' | 'ready' | 'error'>
}

export interface EvaluateRequest {
  corpus_id: string
  strategy: StrategyId
  questions: string[]
  compression_enabled: boolean
}

export interface EvaluateResponse {
  run_id: string
  message: string
}

export interface EvalStatusResponse {
  run_id: string
  status: 'pending' | 'running' | 'complete' | 'error'
}

export interface StrategyMetrics {
  strategy: StrategyId
  context_precision: number
  context_recall: number
  faithfulness: number
  answer_relevancy: number
  avg_latency_ms: number
  cost_inr: number
  compression_ratio: number | null
}

export interface ResultsResponse {
  corpus_id: string
  strategies: StrategyMetrics[]
}

export interface RunListItem {
  run_id: string
  corpus_id: string
  strategy: StrategyId
  status: string
  compression_enabled: boolean
  created_at: string
}

export interface ChunkResult {
  text: string
  score: number
  chunk_id: string
}

export interface StrategyExplorerResult {
  strategy: StrategyId
  answer: string
  chunks: ChunkResult[]
  tokens_raw: number
  tokens_compressed: number | null
  latency_ms: number
}

export interface ExplorerRequest {
  corpus_id: string
  question: string
  compression_enabled: boolean
}

export interface ExplorerResponse {
  question: string
  results: StrategyExplorerResult[]
}
