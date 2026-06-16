from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas import ExplorerRequest, ExplorerResponse

router = APIRouter()


@router.post("/explorer", response_model=ExplorerResponse)
async def explorer(request: ExplorerRequest, db: AsyncSession = Depends(get_db)):
    # TODO: Milestone 2 — retrieve + generate for all 3 strategies (no RAGAS)
    # TODO: Milestone 3 — add optional ScaleDown compression
    return ExplorerResponse(fixed=None, sentence_window=None, hierarchical=None)
