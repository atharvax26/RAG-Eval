from pydantic import BaseModel
from typing import Optional, List, Dict


# ── Ingest ──────────────────────────────────────────────────────────────────

class IngestRequest(BaseModel):
    corpus_name: str
    source_url: str                          # FIX 1a: was `source`
    source_type: str                         # 'pdf' | 'url' | 'web' | 'text'
    strategies: List[str] = ["fixed", "sentence_window", "hierarchical"]


class IngestResponse(BaseModel):
    corpus_id: str
    message: str


class IngestStatusResponse(BaseModel):
    corpus_id: str
    strategy_statuses: Dict[str, str]        # FIX 1b: was `strategies: Dict[str, StrategyStatus]`
                                             # value is plain string: 'pending'|'indexing'|'ready'|'error'


# ── Evaluate ─────────────────────────────────────────────────────────────────

class EvaluateRequest(BaseModel):
    corpus_id: str
    strategy: str                            # single strategy per call (matches frontend)
    questions: List[str]
    compression_enabled: bool = False
    compression_rate: float = 1.0


class EvaluateResponse(BaseModel):
    run_id: str                              # single run_id (matches frontend EvaluateResponse)
    message: str


class EvalStatusResponse(BaseModel):
    run_id: str
    status: str                              # 'pending'|'running'|'complete'|'error'
    progress: int = 0
    total: int = 0


# ── Results ──────────────────────────────────────────────────────────────────

class StrategyMetrics(BaseModel):
    strategy: str                            # added — needed for array response
    context_precision: Optional[float] = None
    context_recall: Optional[float] = None
    faithfulness: Optional[float] = None
    answer_relevancy: Optional[float] = None
    avg_latency_ms: Optional[float] = None
    cost_inr: Optional[float] = None
    compression_ratio: Optional[float] = None  # FIX: was compression_rate


class ResultsResponse(BaseModel):
    corpus_id: str
    strategies: List[StrategyMetrics]        # FIX 1c: was Dict[str, StrategyMetrics]


# ── Runs ──────────────────────────────────────────────────────────────────────

class RunListItem(BaseModel):
    run_id: str                              # FIX: was `id`
    corpus_id: str
    strategy: str
    status: str
    compression_enabled: bool
    created_at: str


# ── Explorer ─────────────────────────────────────────────────────────────────

class ChunkResult(BaseModel):
    text: str
    score: float
    chunk_id: str                            # added — matches frontend ChunkResult


class StrategyExplorerResult(BaseModel):
    strategy: str                            # added — matches frontend StrategyExplorerResult
    answer: str
    chunks: List[ChunkResult]
    tokens_raw: int
    tokens_compressed: Optional[int] = None
    latency_ms: int


class ExplorerRequest(BaseModel):
    corpus_id: str
    question: str
    compression_enabled: bool = False


class ExplorerResponse(BaseModel):
    question: str                            # FIX: was fixed/sentence_window/hierarchical named fields
    results: List[StrategyExplorerResult]    # array matching frontend ExplorerResponse
