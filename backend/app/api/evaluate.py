import asyncio
import time
import uuid
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db, AsyncSessionLocal
from app.models import EvalRun, Query
from app.schemas import EvaluateRequest, EvaluateResponse, EvalStatusResponse
from app.core.retriever import retrieve
from app.core.generator import generate_answer
from app.core.compressor import compress_context
from app.core.evaluator import run_ragas

router = APIRouter()

# In-memory progress tracker: run_id → {"current": int, "total": int}
_progress: dict[str, dict] = {}


@router.post("/evaluate", response_model=EvaluateResponse)
async def start_evaluate(
    request: EvaluateRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    run_id = str(uuid.uuid4())
    _progress[run_id] = {"current": 0, "total": len(request.questions)}
    background_tasks.add_task(_run_evaluation, run_id, request)
    return EvaluateResponse(
        run_id=run_id,
        message=f"Evaluation started for strategy: {request.strategy}",
    )


@router.get("/evaluate/{run_id}/status", response_model=EvalStatusResponse)
async def evaluate_status(run_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(EvalRun).where(EvalRun.id == UUID(run_id))
    )
    run = result.scalar_one_or_none()
    if run is None:
        prog = _progress.get(run_id, {"current": 0, "total": 0})
        return EvalStatusResponse(
            run_id=run_id,
            status="pending",
            progress=prog["current"],
            total=prog["total"],
        )
    prog = _progress.get(run_id, {"current": 0, "total": 0})
    return EvalStatusResponse(
        run_id=run_id,
        status=run.status,
        progress=prog["current"],
        total=prog["total"],
    )


# ── Background task ───────────────────────────────────────────────────────────

async def _run_evaluation(run_id: str, request: EvaluateRequest) -> None:
    async with AsyncSessionLocal() as db:
        # Create eval_run row
        run = EvalRun(
            id=UUID(run_id),
            corpus_id=UUID(request.corpus_id),
            strategy=request.strategy,
            compression_enabled=request.compression_enabled,
            status="running",
            query_count=len(request.questions),
        )
        db.add(run)
        await db.commit()

    try:
        questions = request.questions
        total = len(questions)

        answers: list[str] = []
        contexts: list[list[str]] = []
        latencies: list[float] = []
        tokens_raw_list: list[int] = []
        tokens_compressed_list: list[int] = []
        query_rows: list[dict] = []

        for i, question in enumerate(questions):
            t0 = time.monotonic()

            # Retrieve top-5 chunks
            chunks = await retrieve(request.corpus_id, request.strategy, question, top_k=5)
            raw_context = "\n\n".join(c["text"] for c in chunks)

            # Optionally compress
            if request.compression_enabled:
                loop = asyncio.get_running_loop()
                compressed_text, tok_raw, tok_compressed = await loop.run_in_executor(
                    None, compress_context, raw_context, question
                )
                context_for_gen = compressed_text
            else:
                context_for_gen = raw_context
                tok_raw = max(1, len(raw_context) // 4)
                tok_compressed = tok_raw

            # Generate answer
            loop = asyncio.get_running_loop()
            answer = await loop.run_in_executor(None, generate_answer, question, context_for_gen)

            latency_ms = (time.monotonic() - t0) * 1000

            answers.append(answer)
            contexts.append([c["text"] for c in chunks])
            latencies.append(latency_ms)
            tokens_raw_list.append(tok_raw)
            tokens_compressed_list.append(tok_compressed)
            query_rows.append({
                "question": question,
                "answer": answer,
                "retrieved_chunks": chunks,
                "tokens_raw": tok_raw,
                "tokens_compressed": tok_compressed,
                "latency_ms": latency_ms,
            })

            # Update in-memory progress
            _progress[run_id] = {"current": i + 1, "total": total}

        # Run RAGAS (sync, slow — run in executor)
        loop = asyncio.get_running_loop()
        scores = await loop.run_in_executor(None, run_ragas, questions, answers, contexts)

        total_raw = sum(tokens_raw_list)
        total_compressed = sum(tokens_compressed_list)
        avg_latency = sum(latencies) / len(latencies) if latencies else 0.0
        # Gemini Flash pricing ≈ $0.075/1M input tokens → ×83 INR/USD ≈ ₹0.000006225/token
        cost_inr = total_raw * 0.000006225
        compression_ratio = total_compressed / total_raw if total_raw > 0 else 1.0

        # Persist results
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(EvalRun).where(EvalRun.id == UUID(run_id)))
            run = result.scalar_one()
            run.status = "complete"
            run.context_precision = scores["context_precision"]
            run.context_recall = scores["context_recall"]
            run.faithfulness = scores["faithfulness"]
            run.answer_relevancy = scores["answer_relevancy"]
            run.avg_latency_ms = avg_latency
            run.total_tokens_raw = total_raw
            run.total_tokens_compressed = total_compressed
            run.cost_inr = cost_inr
            run.compression_rate = compression_ratio

            # Insert per-query rows
            for j, qdata in enumerate(query_rows):
                q = Query(
                    run_id=UUID(run_id),
                    question=qdata["question"],
                    answer=qdata["answer"],
                    retrieved_chunks=qdata["retrieved_chunks"],
                    tokens_raw=qdata["tokens_raw"],
                    tokens_compressed=qdata["tokens_compressed"],
                    latency_ms=qdata["latency_ms"],
                )
                db.add(q)

            await db.commit()

    except Exception as exc:
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(EvalRun).where(EvalRun.id == UUID(run_id)))
            run = result.scalar_one_or_none()
            if run:
                run.status = "error"
                await db.commit()
        _progress.pop(run_id, None)
        raise
