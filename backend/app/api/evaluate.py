import uuid
from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas import EvaluateRequest, EvaluateResponse, EvaluateStatusResponse

router = APIRouter()


@router.post("/evaluate", response_model=EvaluateResponse)
async def evaluate(
    request: EvaluateRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    run_ids = {s: str(uuid.uuid4()) for s in request.strategies}
    # CONSTRAINT: evaluation runs as BackgroundTask — never synchronous
    # RAGAS evaluation on 20 questions can take 90+ seconds
    background_tasks.add_task(_run_evaluation, run_ids, request)
    return EvaluateResponse(run_ids=run_ids, status="evaluating")


@router.get("/evaluate/{run_id}/status", response_model=EvaluateStatusResponse)
async def evaluate_status(run_id: str, db: AsyncSession = Depends(get_db)):
    # TODO: Milestone 3 — query eval_runs table for status + progress
    return EvaluateStatusResponse(
        run_id=run_id,
        strategy="",
        status="pending",
        progress=0,
        total=0,
        current_scores={},
    )


async def _run_evaluation(run_ids: dict, request: EvaluateRequest) -> None:
    # TODO: Milestone 3 — RAGAS evaluation pipeline per strategy
    # For each strategy: retrieve → (optionally compress) → generate → RAGAS score → store
    pass
