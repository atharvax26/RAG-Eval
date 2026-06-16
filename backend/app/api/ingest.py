import uuid
from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas import IngestRequest, IngestResponse, IngestStatusResponse, StrategyStatus

router = APIRouter()


@router.post("/ingest", response_model=IngestResponse)
async def ingest_corpus(
    request: IngestRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    corpus_id = str(uuid.uuid4())
    background_tasks.add_task(_run_ingest, corpus_id, request)
    return IngestResponse(
        corpus_id=corpus_id,
        status="ingesting",
        message=f"Ingestion started for strategies: {', '.join(request.strategies)}",
    )


@router.get("/ingest/{corpus_id}/status", response_model=IngestStatusResponse)
async def ingest_status(corpus_id: str, db: AsyncSession = Depends(get_db)):
    # TODO: Milestone 1 — query chunk_indexes table for this corpus_id
    return IngestStatusResponse(corpus_id=corpus_id, strategies={
        s: StrategyStatus(status="pending", chunk_count=0)
        for s in ["fixed", "sentence_window", "hierarchical"]
    })


async def _run_ingest(corpus_id: str, request: IngestRequest) -> None:
    # TODO: Milestone 1 — implement single strategy (fixed)
    # TODO: Milestone 2 — asyncio.gather all 3 strategies
    pass
