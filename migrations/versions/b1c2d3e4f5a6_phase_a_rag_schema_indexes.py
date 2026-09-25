"""Phase A: document metadata, chunk_index, tsvector GIN, HNSW index

Revision ID: b1c2d3e4f5a6
Revises: e911c7329457
Create Date: 2026-09-25 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b1c2d3e4f5a6"
down_revision: Union[str, None] = "e911c7329457"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("documents", sa.Column("content_sha256", sa.String(length=64), nullable=True))
    op.add_column("documents", sa.Column("embedding_model", sa.String(length=256), nullable=True))
    op.add_column(
        "documents",
        sa.Column("chunk_count", sa.Integer(), nullable=False, server_default="0"),
    )
    op.add_column("documents", sa.Column("error_message", sa.Text(), nullable=True))

    op.add_column("document_chunks", sa.Column("chunk_index", sa.Integer(), nullable=True))

    op.drop_column("document_chunks", "content_tsvector")
    op.execute(
        """
        ALTER TABLE document_chunks
        ADD COLUMN content_tsvector tsvector
        GENERATED ALWAYS AS (to_tsvector('english', coalesce(content, ''))) STORED
        """
    )
    op.execute(
        "CREATE INDEX ix_document_chunks_content_tsvector "
        "ON document_chunks USING GIN (content_tsvector)"
    )

    op.execute(
        """
        CREATE INDEX ix_document_chunks_embedding_hnsw
        ON document_chunks USING hnsw (embedding vector_cosine_ops)
        """
    )
    op.execute(
        """
        CREATE INDEX ix_documents_kb_status
        ON documents (knowledge_base_id, status)
        """
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_documents_kb_status")
    op.execute("DROP INDEX IF EXISTS ix_document_chunks_embedding_hnsw")
    op.execute("DROP INDEX IF EXISTS ix_document_chunks_content_tsvector")
    op.drop_column("document_chunks", "content_tsvector")
    op.add_column(
        "document_chunks",
        sa.Column("content_tsvector", sa.Text(), nullable=True),
    )

    op.drop_column("document_chunks", "chunk_index")
    op.drop_column("documents", "error_message")
    op.drop_column("documents", "chunk_count")
    op.drop_column("documents", "embedding_model")
    op.drop_column("documents", "content_sha256")
