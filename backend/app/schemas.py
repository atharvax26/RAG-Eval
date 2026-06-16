from pydantic import BaseModel
from typing import Optional, List, Dict


class IngestRequest(BaseModel):
    corpus_name: str
    source: str
    source_type: str  # 'url' | 'pdf' | 'text'
    strategies: List[str] = ["fixed", "sentence_window", "hierarchical"]


class IngestResponse(BaseModel):
    corpus_id: str
    status: str
    message: str


class StrategyStatus(BaseModel):
    status: str
    chunk_count: int


class IngestStatusResponse(BaseModel):
    corpus_id: str
    strategies: Dict[str, StrategyStatus]


class EvaluateRequest(BaseModel):
    corpus_id: str
    questions: List[str]
    strategies: List[str] = ["fixed", "sentence_window", "hierarchical"]
    compression_enabled: bool = False
    compression_rate: float = 1.0  # 0.3–1.0


class EvaluateResponse(BaseModel):
    run_ids: Dict[str, str]
    status: str


class EvaluateStatusResponse(BaseModel):
    run_id: str
    strategy: str
    status: str
    progress: int
    total: int
    current_scores: Dict


class StrategyMetrics(BaseModel):
    context_precision: Optional[float] = None
    context_recall: Optional[float] = None
    faithfulness: Optional[float] = None
    answer_relevancy: Optional[float] = None
    avg_latency_ms: Optional[int] = None
    tokens_raw: Optional[int] = None
    tokens_compressed: Optional[int] = None
    cost_inr: Optional[float] = None
    compression_rate: Optional[float] = None


class ResultsResponse(BaseModel):
    corpus_id: str
    strategies: Dict[str, StrategyMetrics]


class RunListItem(BaseModel):
    id: str
    corpus_id: str
    strategy: str
    compression_enabled: bool
    faithfulness: Optional[float] = None
    cost_inr: Optional[float] = None
    created_at: str


class ChunkResult(BaseModel):
    text: str
    score: float


class StrategyExplorerResult(BaseModel):
    answer: str
    chunks: List[ChunkResult]
    tokens_raw: int
    tokens_compressed: int
    latency_ms: int


class ExplorerRequest(BaseModel):
    corpus_id: str
    question: str
    compression_enabled: bool = False


class ExplorerResponse(BaseModel):
    fixed: Optional[StrategyExplorerResult] = None
    sentence_window: Optional[StrategyExplorerResult] = None
    hierarchical: Optional[StrategyExplorerResult] = None
