from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import EvalRun
from app.schemas import RunListItem

router = APIRouter()


@router.get("/runs", response_model=List[RunListItem])
async def list_runs(
    corpus_id: Optional[str] = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    q = select(EvalRun).order_by(EvalRun.created_at.desc()).limit(limit).offset(offset)
    if corpus_id:
        q = q.where(EvalRun.corpus_id == UUID(corpus_id))

    result = await db.execute(q)
    runs = result.scalars().all()

    return [
        RunListItem(
            run_id=str(run.id),
            corpus_id=str(run.corpus_id),
            strategy=run.strategy,
            status=run.status,
            compression_enabled=run.compression_enabled,
            created_at=run.created_at.isoformat() if run.created_at else "",
        )
        for run in runs
    ]
