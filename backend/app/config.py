from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    GEMINI_API_KEY: str = ""
    SCALEDOWN_API_KEY: str = ""
    DATABASE_URL: str = "postgresql+asyncpg://postgres:rageval123@db:5432/rageval"
    DATABASE_URL_SYNC: str = "postgresql://postgres:rageval123@db:5432/rageval"
    QDRANT_HOST: str = "qdrant"
    QDRANT_PORT: int = 6333
    QDRANT_COLLECTION_PREFIX: str = "rageval_"
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    EMBEDDING_MODEL: str = "models/text-embedding-004"
    GENERATION_MODEL: str = "gemini-1.5-flash"
    EMBED_DIM: int = 768

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
