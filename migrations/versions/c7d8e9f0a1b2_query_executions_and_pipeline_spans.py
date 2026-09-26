"""Add query_executions and pipeline_spans for RAG history and observability.

Revision ID: c7d8e9f0a1b2
Revises: b1c2d3e4f5a6
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "c7d8e9f0a1b2"
down_revision: Union[str, None] = "b1c2d3e4f5a6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "query_executions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("knowledge_base_id", sa.Integer(), nullable=False),
        sa.Column("question", sa.Text(), nullable=False),
        sa.Column("answer", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("request_id", sa.String(length=64), nullable=True),
        sa.Column("otel_trace_id", sa.String(length=128), nullable=True),
        sa.Column("routed_model", sa.String(length=256), nullable=True),
        sa.Column("routing_policy", sa.String(length=64), nullable=True),
        sa.Column("routing_reason", sa.String(length=512), nullable=True),
        sa.Column("prompt_tokens", sa.Integer(), nullable=True),
        sa.Column("completion_tokens", sa.Integer(), nullable=True),
        sa.Column("total_tokens", sa.Integer(), nullable=True),
        sa.Column("estimated_cost_usd", sa.Numeric(precision=12, scale=6), nullable=True),
        sa.Column("chunks_retrieved", sa.Integer(), nullable=True),
        sa.Column("citations", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("latency_ms", sa.Numeric(precision=12, scale=3), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["knowledge_base_id"], ["knowledge_bases.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_query_executions_user_kb_created",
        "query_executions",
        ["user_id", "knowledge_base_id", "created_at"],
    )

    op.create_table(
        "pipeline_spans",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("execution_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("parent_span_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("name", sa.String(length=256), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("started_at", sa.DateTime(), nullable=False),
        sa.Column("ended_at", sa.DateTime(), nullable=True),
        sa.Column("latency_ms", sa.Numeric(precision=12, scale=3), nullable=True),
        sa.Column("model", sa.String(length=256), nullable=True),
        sa.Column("tokens", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("attributes", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("input_preview", sa.Text(), nullable=True),
        sa.Column("output_preview", sa.Text(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["execution_id"], ["query_executions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["parent_span_id"], ["pipeline_spans.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_pipeline_spans_execution_id", "pipeline_spans", ["execution_id"])


def downgrade() -> None:
    op.drop_index("ix_pipeline_spans_execution_id", table_name="pipeline_spans")
    op.drop_table("pipeline_spans")
    op.drop_index("ix_query_executions_user_kb_created", table_name="query_executions")
    op.drop_table("query_executions")
