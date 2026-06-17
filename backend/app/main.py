from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api import ingest, evaluate, results, runs, explorer

app = FastAPI(title="RAG Eval Studio", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ingest.router, prefix="/api")
app.include_router(evaluate.router, prefix="/api")
app.include_router(results.router, prefix="/api")
app.include_router(runs.router, prefix="/api")
app.include_router(explorer.router, prefix="/api")


@app.get("/api/health")
async def health():
    # Check DB
    db_status = "disconnected"
    try:
        from app.database import AsyncSessionLocal
        from sqlalchemy import text
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception:
        pass

    # Check Qdrant
    qdrant_status = "disconnected"
    try:
        from qdrant_client import AsyncQdrantClient
        client = AsyncQdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT)
        await client.get_collections()
        qdrant_status = "connected"
    except Exception:
        pass

    return {"status": "ok", "db": db_status, "qdrant": qdrant_status}
