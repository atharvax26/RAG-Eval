from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas import ResultsResponse

router = APIRouter()


@router.get("/results/{corpus_id}", response_model=ResultsResponse)
async def get_results(
    corpus_id: str,
    strategies: str = Query(default="fixed,sentence_window,hierarchical"),
    db: AsyncSession = Depends(get_db),
):
    # TODO: Milestone 3 — aggregate RAGAS scores from eval_runs + queries tables
    return ResultsResponse(corpus_id=corpus_id, strategies={})
