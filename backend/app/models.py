import uuid
from sqlalchemy import Column, Integer, Float, Boolean, DateTime, ForeignKey, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from app.database import Base


class Corpus(Base):
    __tablename__ = "corpora"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(Text, nullable=False)
    source_url = Column(Text)
    source_type = Column(Text, nullable=False)  # 'url' | 'pdf' | 'text'
    doc_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ChunkIndex(Base):
    __tablename__ = "chunk_indexes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    corpus_id = Column(UUID(as_uuid=True), ForeignKey("corpora.id", ondelete="CASCADE"), nullable=False)
    strategy = Column(Text, nullable=False)  # 'fixed' | 'sentence_window' | 'hierarchical'
    chunk_count = Column(Integer, default=0)
    qdrant_collection = Column(Text, unique=True)
    status = Column(Text, default="pending")  # 'pending'|'indexing'|'ready'|'error'
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (UniqueConstraint("corpus_id", "strategy"),)


class EvalRun(Base):
    __tablename__ = "eval_runs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    corpus_id = Column(UUID(as_uuid=True), ForeignKey("corpora.id"), nullable=False)
    strategy = Column(Text, nullable=False)
    compression_enabled = Column(Boolean, default=False)
    compression_rate = Column(Float)
    context_precision = Column(Float)
    context_recall = Column(Float)
    faithfulness = Column(Float)
    answer_relevancy = Column(Float)
    avg_latency_ms = Column(Integer)
    total_tokens_raw = Column(Integer)
    total_tokens_compressed = Column(Integer)
    cost_inr = Column(Float)
    query_count = Column(Integer, default=0)
    status = Column(Text, default="pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Query(Base):
    __tablename__ = "queries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    run_id = Column(UUID(as_uuid=True), ForeignKey("eval_runs.id", ondelete="CASCADE"), nullable=False)
    question = Column(Text, nullable=False)
    answer = Column(Text)
    retrieved_chunks = Column(JSONB)  # list of {text, score, chunk_id}
    context_precision = Column(Float)
    context_recall = Column(Float)
    faithfulness = Column(Float)
    answer_relevancy = Column(Float)
    tokens_raw = Column(Integer)
    tokens_compressed = Column(Integer)
    latency_ms = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
