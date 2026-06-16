from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance, VectorParams
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.core import StorageContext, VectorStoreIndex
from app.config import settings


def collection_name(corpus_id: str, strategy: str) -> str:
    # IMPORTANT: use this naming everywhere — never hardcode
    return f"{settings.QDRANT_COLLECTION_PREFIX}{corpus_id}_{strategy}"


async def build_index(corpus_id: str, strategy: str, nodes, embed_model):
    client = AsyncQdrantClient(
        host=settings.QDRANT_HOST, port=settings.QDRANT_PORT
    )
    cname = collection_name(corpus_id, strategy)
    await client.recreate_collection(
        collection_name=cname,
        vectors_config=VectorParams(size=768, distance=Distance.COSINE),
    )
    vector_store = QdrantVectorStore(client=client, collection_name=cname)
    storage_ctx = StorageContext.from_defaults(vector_store=vector_store)
    index = VectorStoreIndex(
        nodes,
        storage_context=storage_ctx,
        embed_model=embed_model,
        show_progress=True,
    )
    return index


async def load_index(corpus_id: str, strategy: str, embed_model):
    client = AsyncQdrantClient(
        host=settings.QDRANT_HOST, port=settings.QDRANT_PORT
    )
    cname = collection_name(corpus_id, strategy)
    vector_store = QdrantVectorStore(client=client, collection_name=cname)
    storage_ctx = StorageContext.from_defaults(vector_store=vector_store)
    return VectorStoreIndex.from_vector_store(vector_store, embed_model=embed_model)
