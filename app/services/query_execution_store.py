from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.pipeline_span import PipelineSpan
from app.models.query_execution import QueryExecution

PREVIEW_MAX_LEN = 500


def _preview(text: str | None) -> str | None:
    if text is None:
        return None
    cleaned = text.strip()
    if not cleaned:
        return None
    if len(cleaned) <= PREVIEW_MAX_LEN:
        return cleaned
    return cleaned[: PREVIEW_MAX_LEN - 3] + "..."


class QueryExecutionStore:
    def create_execution(
        self,
        db: Session,
        *,
        user_id: int,
        knowledge_base_id: int,
        question: str,
        request_id: str | None = None,
        otel_trace_id: str | None = None,
    ) -> QueryExecution:
        row = QueryExecution(
            user_id=user_id,
            knowledge_base_id=knowledge_base_id,
            question=question,
            status="running",
            request_id=request_id,
            otel_trace_id=otel_trace_id,
        )
        db.add(row)
        db.commit()
        db.refresh(row)
        return row

    def start_span(
        self,
        db: Session,
        *,
        execution_id: UUID,
        name: str,
        parent_span_id: UUID | None = None,
        attributes: dict[str, Any] | None = None,
        input_preview: str | None = None,
    ) -> PipelineSpan:
        span = PipelineSpan(
            execution_id=execution_id,
            parent_span_id=parent_span_id,
            name=name,
            status="running",
            attributes=attributes or {},
            input_preview=_preview(input_preview),
        )
        db.add(span)
        db.commit()
        db.refresh(span)
        return span

    def complete_span(
        self,
        db: Session,
        span: PipelineSpan,
        *,
        status: str = "completed",
        output_preview: str | None = None,
        model: str | None = None,
        tokens: dict[str, Any] | None = None,
        attributes: dict[str, Any] | None = None,
        error_message: str | None = None,
    ) -> PipelineSpan:
        ended = datetime.utcnow()
        latency_ms = (ended - span.started_at).total_seconds() * 1000
        span.status = status
        span.ended_at = ended
        span.latency_ms = Decimal(str(round(latency_ms, 3)))
        if output_preview is not None:
            span.output_preview = _preview(output_preview)
        if model is not None:
            span.model = model
        if tokens is not None:
            span.tokens = tokens
        if attributes:
            merged = dict(span.attributes or {})
            merged.update(attributes)
            span.attributes = merged
        if error_message:
            span.error_message = error_message[:2000]
        db.add(span)
        db.commit()
        db.refresh(span)
        return span

    def finalize_execution(
        self,
        db: Session,
        execution: QueryExecution,
        *,
        status: str,
        answer: str | None = None,
        citations: list[dict[str, Any]] | None = None,
        chunks_retrieved: int | None = None,
        routed_model: str | None = None,
        routing_policy: str | None = None,
        routing_reason: str | None = None,
        prompt_tokens: int | None = None,
        completion_tokens: int | None = None,
        total_tokens: int | None = None,
        estimated_cost_usd: float | Decimal | None = None,
        latency_ms: float | None = None,
        error_message: str | None = None,
    ) -> QueryExecution:
        execution.status = status
        execution.answer = answer
        execution.citations = citations
        execution.chunks_retrieved = chunks_retrieved
        execution.routed_model = routed_model
        execution.routing_policy = routing_policy
        execution.routing_reason = routing_reason
        execution.prompt_tokens = prompt_tokens
        execution.completion_tokens = completion_tokens
        execution.total_tokens = total_tokens
        if estimated_cost_usd is not None:
            execution.estimated_cost_usd = Decimal(str(estimated_cost_usd))
        if latency_ms is not None:
            execution.latency_ms = Decimal(str(round(latency_ms, 3)))
        if error_message:
            execution.error_message = error_message[:2000]
        db.add(execution)
        db.commit()
        db.refresh(execution)
        return execution

    def get_execution(
        self,
        db: Session,
        execution_id: UUID,
        *,
        user_id: int,
        knowledge_base_id: int,
    ) -> QueryExecution | None:
        return (
            db.query(QueryExecution)
            .filter(
                QueryExecution.id == execution_id,
                QueryExecution.user_id == user_id,
                QueryExecution.knowledge_base_id == knowledge_base_id,
            )
            .first()
        )

    def list_executions(
        self,
        db: Session,
        *,
        user_id: int,
        knowledge_base_id: int,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[QueryExecution], int]:
        q = db.query(QueryExecution).filter(
            QueryExecution.user_id == user_id,
            QueryExecution.knowledge_base_id == knowledge_base_id,
        )
        total = q.count()
        items = (
            q.order_by(QueryExecution.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
        return items, total

    def list_spans(self, db: Session, execution_id: UUID) -> list[PipelineSpan]:
        return (
            db.query(PipelineSpan)
            .filter(PipelineSpan.execution_id == execution_id)
            .order_by(PipelineSpan.started_at.asc())
            .all()
        )


query_execution_store = QueryExecutionStore()
