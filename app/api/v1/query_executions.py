from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.security import get_current_active_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.query_execution import (
    ExecutionTraceView,
    PaginatedQueryExecutions,
    QueryExecutionDetail,
    QueryExecutionListItem,
    SpanView,
)
from app.schemas.rag import Citation, TokenUsage
from app.services.knowledge_base import get_knowledge_base
from app.services.query_execution_store import query_execution_store

router = APIRouter()


def _authorize_kb(db: Session, user_id: int, kb_id: int, current_user: User) -> None:
    if current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    db_kb = get_knowledge_base(db, kb_id=kb_id)
    if db_kb is None or db_kb.owner_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Knowledge Base not found")


@router.get(
    "/users/{user_id}/knowledge_bases/{kb_id}/queries",
    response_model=PaginatedQueryExecutions,
)
def list_query_executions(
    user_id: int,
    kb_id: int,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    _authorize_kb(db, user_id, kb_id, current_user)
    items, total = query_execution_store.list_executions(
        db, user_id=user_id, knowledge_base_id=kb_id, limit=limit, offset=offset
    )
    return PaginatedQueryExecutions(
        items=[
            QueryExecutionListItem(
                execution_id=row.id,
                question=row.question,
                status=row.status,
                routed_model=row.routed_model,
                total_tokens=row.total_tokens,
                estimated_cost_usd=float(row.estimated_cost_usd) if row.estimated_cost_usd else None,
                latency_ms=float(row.latency_ms) if row.latency_ms else None,
                created_at=row.created_at,
            )
            for row in items
        ],
        limit=limit,
        offset=offset,
        total=total,
        has_more=offset + len(items) < total,
    )


@router.get(
    "/users/{user_id}/knowledge_bases/{kb_id}/queries/{execution_id}",
    response_model=QueryExecutionDetail,
)
def get_query_execution(
    user_id: int,
    kb_id: int,
    execution_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    _authorize_kb(db, user_id, kb_id, current_user)
    row = query_execution_store.get_execution(
        db, execution_id, user_id=user_id, knowledge_base_id=kb_id
    )
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Query execution not found")

    citations = [Citation(**c) for c in (row.citations or [])]
    return QueryExecutionDetail(
        execution_id=row.id,
        knowledge_base_id=row.knowledge_base_id,
        question=row.question,
        answer=row.answer,
        status=row.status,
        routed_model=row.routed_model,
        routing_policy=row.routing_policy,
        routing_reason=row.routing_reason,
        usage=TokenUsage(
            prompt_tokens=row.prompt_tokens,
            completion_tokens=row.completion_tokens,
            total_tokens=row.total_tokens,
        ),
        estimated_cost_usd=float(row.estimated_cost_usd) if row.estimated_cost_usd else None,
        latency_ms=float(row.latency_ms) if row.latency_ms else None,
        chunks_retrieved=row.chunks_retrieved,
        citations=citations,
        request_id=row.request_id,
        otel_trace_id=row.otel_trace_id,
        error_message=row.error_message,
        created_at=row.created_at,
    )


@router.get(
    "/users/{user_id}/knowledge_bases/{kb_id}/queries/{execution_id}/trace",
    response_model=ExecutionTraceView,
)
def get_query_execution_trace(
    user_id: int,
    kb_id: int,
    execution_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    _authorize_kb(db, user_id, kb_id, current_user)
    row = query_execution_store.get_execution(
        db, execution_id, user_id=user_id, knowledge_base_id=kb_id
    )
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Query execution not found")

    spans = query_execution_store.list_spans(db, execution_id)
    span_views = [
        SpanView(
            span_id=s.id,
            parent_span_id=s.parent_span_id,
            name=s.name,
            status=s.status,
            started_at=s.started_at,
            ended_at=s.ended_at,
            latency_ms=float(s.latency_ms) if s.latency_ms else None,
            model=s.model,
            tokens=s.tokens,
            attributes=s.attributes or {},
            input_preview=s.input_preview,
            output_preview=s.output_preview,
            error_message=s.error_message,
        )
        for s in spans
    ]
    completed_at = max((s.ended_at for s in spans if s.ended_at), default=None)
    return ExecutionTraceView(
        execution_id=row.id,
        started_at=row.created_at,
        completed_at=completed_at,
        total_latency_ms=float(row.latency_ms) if row.latency_ms else None,
        spans=span_views,
    )
