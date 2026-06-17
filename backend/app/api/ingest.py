import asyncio
import re
import tempfile
import os
from pathlib import Path
from uuid import UUID

import httpx
from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db, AsyncSessionLocal
from app.models import Corpus, ChunkIndex
from app.schemas import IngestRequest, IngestResponse, IngestStatusResponse
from app.core.chunkers import get_nodes
from app.core.embedder import get_embed_model
from app.core.indexer import build_index, collection_name

router = APIRouter()


@router.post("/ingest", response_model=IngestResponse)
async def ingest_corpus(
    request: IngestRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    import uuid
    corpus_id = str(uuid.uuid4())
    background_tasks.add_task(_run_ingest, corpus_id, request)
    return IngestResponse(
        corpus_id=corpus_id,
        message=f"Ingestion started for strategies: {', '.join(request.strategies)}",
    )


@router.get("/ingest/{corpus_id}/status", response_model=IngestStatusResponse)
async def ingest_status(corpus_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ChunkIndex).where(ChunkIndex.corpus_id == UUID(corpus_id))
    )
    rows = result.scalars().all()
    statuses = {row.strategy: row.status for row in rows}
    # If rows not yet created, show pending for all known strategies
    if not statuses:
        statuses = {s: "pending" for s in ["fixed", "sentence_window", "hierarchical"]}
    return IngestStatusResponse(corpus_id=corpus_id, strategy_statuses=statuses)


# ── Document loading ──────────────────────────────────────────────────────────

def _load_documents(source_url: str, source_type: str):
    from llama_index.core.schema import Document

    stype = source_type.lower()

    if stype in ("url", "web"):
        resp = httpx.get(source_url, follow_redirects=True, timeout=30)
        resp.raise_for_status()
        # Strip HTML tags to get plain text
        text = re.sub(r"<script[^>]*>.*?</script>", " ", resp.text, flags=re.DOTALL)
        text = re.sub(r"<style[^>]*>.*?</style>", " ", text, flags=re.DOTALL)
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        return [Document(text=text, metadata={"source": source_url})]

    elif stype == "pdf":
        resp = httpx.get(source_url, follow_redirects=True, timeout=60)
        resp.raise_for_status()
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            f.write(resp.content)
            tmp_path = f.name
        try:
            from llama_index.readers.file import PDFReader
            docs = PDFReader().load_data(file=Path(tmp_path))
            return docs
        finally:
            os.unlink(tmp_path)

    elif stype == "text":
        # source_url field contains the raw text when source_type is 'text'
        return [Document(text=source_url, metadata={"source": "direct_text"})]

    else:
        raise ValueError(f"Unknown source_type: {source_type!r}")


# ── Background task ───────────────────────────────────────────────────────────

async def _run_ingest(corpus_id: str, request: IngestRequest) -> None:
    async with AsyncSessionLocal() as db:
        try:
            # 1. Load documents (sync — run in thread to avoid blocking event loop)
            loop = asyncio.get_running_loop()
            documents = await loop.run_in_executor(
                None, _load_documents, request.source_url, request.source_type
            )

            # 2. Insert corpus row
            corpus = Corpus(
                id=UUID(corpus_id),
                name=request.corpus_name,
                source_url=request.source_url,
                source_type=request.source_type,
                doc_count=len(documents),
            )
            db.add(corpus)

            # 3. Insert chunk_index rows as 'pending'
            for strategy in request.strategies:
                ci = ChunkIndex(
                    corpus_id=UUID(corpus_id),
                    strategy=strategy,
                    status="pending",
                    chunk_count=0,
                    qdrant_collection=collection_name(corpus_id, strategy),
                )
                db.add(ci)

            await db.commit()

        except Exception as exc:
            await db.rollback()
            # Can't update rows since they may not exist — just return
            return

    # 4. Index all strategies in parallel, each with its own session
    embed_model = get_embed_model()
    tasks = [
        _index_one_strategy(corpus_id, strategy, documents, embed_model)
        for strategy in request.strategies
    ]
    await asyncio.gather(*tasks, return_exceptions=True)


async def _index_one_strategy(corpus_id: str, strategy: str, documents, embed_model) -> None:
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(ChunkIndex).where(
                ChunkIndex.corpus_id == UUID(corpus_id),
                ChunkIndex.strategy == strategy,
            )
        )
        ci = result.scalar_one_or_none()
        if ci is None:
            return

        try:
            ci.status = "indexing"
            await db.commit()

            # Chunk + build index (sync ops — run in executor)
            loop = asyncio.get_running_loop()
            nodes = await loop.run_in_executor(None, get_nodes, documents, strategy)

            await build_index(corpus_id, strategy, nodes, embed_model)

            ci.status = "ready"
            ci.chunk_count = len(nodes)
            await db.commit()

        except Exception:
            ci.status = "error"
            await db.commit()
