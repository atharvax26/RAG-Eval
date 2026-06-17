import asyncio
import time

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas import ExplorerRequest, ExplorerResponse, StrategyExplorerResult, ChunkResult
from app.core.retriever import retrieve
from app.core.generator import generate_answer
from app.core.compressor import compress_context

router = APIRouter()

STRATEGIES = ["fixed", "sentence_window", "hierarchical"]


@router.post("/explorer", response_model=ExplorerResponse)
async def explorer(request: ExplorerRequest, db: AsyncSession = Depends(get_db)):
    tasks = [
        _query_strategy(request.corpus_id, strategy, request.question, request.compression_enabled)
        for strategy in STRATEGIES
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    strategy_results = []
    for strategy, result in zip(STRATEGIES, results):
        if isinstance(result, Exception):
            strategy_results.append(StrategyExplorerResult(
                strategy=strategy,
                answer="Index not found or query failed.",
                chunks=[],
                tokens_raw=0,
                tokens_compressed=None,
                latency_ms=0,
            ))
        else:
            strategy_results.append(result)

    return ExplorerResponse(question=request.question, results=strategy_results)


async def _query_strategy(
    corpus_id: str,
    strategy: str,
    question: str,
    compression_enabled: bool,
) -> StrategyExplorerResult:
    t0 = time.monotonic()

    try:
        chunks_raw = await retrieve(corpus_id, strategy, question, top_k=5)
    except Exception:
        raise RuntimeError(f"Index not found for strategy: {strategy}")

    raw_context = "\n\n".join(c["text"] for c in chunks_raw)
    tok_raw = max(1, len(raw_context) // 4)

    if compression_enabled:
        loop = asyncio.get_running_loop()
        compressed_text, tok_raw, tok_compressed = await loop.run_in_executor(
            None, compress_context, raw_context, question
        )
        context_for_gen = compressed_text
    else:
        context_for_gen = raw_context
        tok_compressed = None

    loop = asyncio.get_running_loop()
    answer = await loop.run_in_executor(None, generate_answer, question, context_for_gen)

    latency_ms = int((time.monotonic() - t0) * 1000)

    chunks = [
        ChunkResult(text=c["text"], score=c["score"], chunk_id=c["chunk_id"])
        for c in chunks_raw
    ]

    return StrategyExplorerResult(
        strategy=strategy,
        answer=answer,
        chunks=chunks,
        tokens_raw=tok_raw,
        tokens_compressed=tok_compressed,
        latency_ms=latency_ms,
    )
