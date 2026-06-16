"""Initial schema

Revision ID: 0001
Revises:
Create Date: 2026-06-16 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # pgcrypto needed for gen_random_uuid()
    op.execute('CREATE EXTENSION IF NOT EXISTS pgcrypto')

    op.create_table(
        'corpora',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('source_url', sa.Text, nullable=False),
        sa.Column('source_type', sa.String(50), nullable=False),
        sa.Column('doc_count', sa.Integer, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        'chunk_indexes',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), primary_key=True),
        sa.Column('corpus_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('corpora.id', ondelete='CASCADE'), nullable=False),
        sa.Column('strategy', sa.String(50), nullable=False),
        sa.Column('chunk_count', sa.Integer, server_default='0'),
        sa.Column('qdrant_collection', sa.String(255), nullable=False, unique=True),
        sa.Column('status', sa.String(50), server_default='pending'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint('corpus_id', 'strategy', name='uq_chunk_index_corpus_strategy'),
    )

    op.create_table(
        'eval_runs',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), primary_key=True),
        sa.Column('corpus_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('corpora.id', ondelete='CASCADE'), nullable=False),
        sa.Column('strategy', sa.String(50), nullable=False),
        sa.Column('compression_enabled', sa.Boolean, server_default='false'),
        sa.Column('compression_rate', sa.Float, nullable=True),
        sa.Column('context_precision', sa.Float, nullable=True),
        sa.Column('context_recall', sa.Float, nullable=True),
        sa.Column('faithfulness', sa.Float, nullable=True),
        sa.Column('answer_relevancy', sa.Float, nullable=True),
        sa.Column('avg_latency_ms', sa.Float, nullable=True),
        sa.Column('total_tokens_raw', sa.Integer, nullable=True),
        sa.Column('total_tokens_compressed', sa.Integer, nullable=True),
        sa.Column('cost_inr', sa.Float, nullable=True),
        sa.Column('query_count', sa.Integer, server_default='0'),
        sa.Column('status', sa.String(50), server_default='pending'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        'queries',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), primary_key=True),
        sa.Column('run_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('eval_runs.id', ondelete='CASCADE'), nullable=False),
        sa.Column('question', sa.Text, nullable=False),
        sa.Column('answer', sa.Text, nullable=True),
        sa.Column('retrieved_chunks', postgresql.JSONB, nullable=True),
        sa.Column('context_precision', sa.Float, nullable=True),
        sa.Column('context_recall', sa.Float, nullable=True),
        sa.Column('faithfulness', sa.Float, nullable=True),
        sa.Column('answer_relevancy', sa.Float, nullable=True),
        sa.Column('tokens_raw', sa.Integer, nullable=True),
        sa.Column('tokens_compressed', sa.Integer, nullable=True),
        sa.Column('latency_ms', sa.Float, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table('queries')
    op.drop_table('eval_runs')
    op.drop_table('chunk_indexes')
    op.drop_table('corpora')
