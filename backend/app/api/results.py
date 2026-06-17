from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import EvalRun
from app.schemas import ResultsResponse, StrategyMetrics

router = APIRouter()


@router.get("/results/{corpus_id}", response_model=ResultsResponse)
async def get_results(
    corpus_id: str,
    strategies: str = Query(default="fixed,sentence_window,hierarchical"),
    db: AsyncSession = Depends(get_db),
):
    requested = [s.strip() for s in strategies.split(",") if s.strip()]

    # Latest completed run per strategy — subquery picks max created_at per strategy
    subq = (
        select(
            EvalRun.strategy,
            func.max(EvalRun.created_at).label("latest"),
        )
        .where(
            EvalRun.corpus_id == UUID(corpus_id),
            EvalRun.status == "complete",
            EvalRun.strategy.in_(requested),
        )
        .group_by(EvalRun.strategy)
        .subquery()
    )

    result = await db.execute(
        select(EvalRun).join(
            subq,
            (EvalRun.strategy == subq.c.strategy) & (EvalRun.created_at == subq.c.latest),
        )
    )
    runs = result.scalars().all()

    metrics_list = []
    for run in runs:
        total_raw = run.total_tokens_raw or 1
        total_comp = run.total_tokens_compressed or total_raw
        metrics_list.append(
            StrategyMetrics(
                strategy=run.strategy,
                context_precision=run.context_precision,
                context_recall=run.context_recall,
                faithfulness=run.faithfulness,
                answer_relevancy=run.answer_relevancy,
                avg_latency_ms=run.avg_latency_ms,
                cost_inr=run.cost_inr,
                compression_ratio=total_comp / total_raw,
            )
        )

    return ResultsResponse(corpus_id=corpus_id, strategies=metrics_list)
