from llama_index.embeddings.gemini import GeminiEmbedding
from app.config import settings


def get_embed_model():
    return GeminiEmbedding(
        model_name=settings.EMBEDDING_MODEL,  # 'models/text-embedding-004'
        api_key=settings.GEMINI_API_KEY,
    )


EMBED_DIM = 768  # text-embedding-004 output dimension — hardcode this
