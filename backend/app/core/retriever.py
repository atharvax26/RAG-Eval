from typing import List, Dict
from app.core.indexer import load_index
from app.core.embedder import get_embed_model


async def retrieve(corpus_id: str, strategy: str, query: str, top_k: int = 5) -> List[Dict]:
    embed_model = get_embed_model()
    index = await load_index(corpus_id, strategy, embed_model)
    retriever = index.as_retriever(similarity_top_k=top_k)
    nodes = retriever.retrieve(query)
    return [
        {"text": n.get_content(), "score": float(n.score or 0.0), "chunk_id": n.node_id}
        for n in nodes
    ]
