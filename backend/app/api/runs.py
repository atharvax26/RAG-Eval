from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.database import get_db
from app.schemas import RunListItem

router = APIRouter()


@router.get("/runs", response_model=List[RunListItem])
async def list_runs(
    corpus_id: Optional[str] = Query(default=None),
    limit: int = Query(default=20),
    offset: int = Query(default=0),
    db: AsyncSession = Depends(get_db),
):
    # TODO: Milestone 3 — paginated query of eval_runs table
    return []
