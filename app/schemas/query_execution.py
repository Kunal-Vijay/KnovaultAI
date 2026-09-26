from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.schemas.rag import Citation, TokenUsage


class QueryExecutionListItem(BaseModel):
    execution_id: UUID
    question: str
    status: str
    routed_model: Optional[str] = None
    total_tokens: Optional[int] = None
    estimated_cost_usd: Optional[float] = None
    latency_ms: Optional[float] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PaginatedQueryExecutions(BaseModel):
    items: list[QueryExecutionListItem]
    limit: int
    offset: int
    total: int
    has_more: bool


class QueryExecutionDetail(BaseModel):
    execution_id: UUID
    knowledge_base_id: int
    question: str
    answer: Optional[str] = None
    status: str
    routed_model: Optional[str] = None
    routing_policy: Optional[str] = None
    routing_reason: Optional[str] = None
    usage: Optional[TokenUsage] = None
    estimated_cost_usd: Optional[float] = None
    latency_ms: Optional[float] = None
    chunks_retrieved: Optional[int] = None
    citations: list[Citation] = []
    request_id: Optional[str] = None
    otel_trace_id: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime


class SpanView(BaseModel):
    span_id: UUID
    parent_span_id: Optional[UUID] = None
    name: str
    status: str
    started_at: datetime
    ended_at: Optional[datetime] = None
    latency_ms: Optional[float] = None
    model: Optional[str] = None
    tokens: Optional[dict[str, Any]] = None
    attributes: dict[str, Any] = {}
    input_preview: Optional[str] = None
    output_preview: Optional[str] = None
    error_message: Optional[str] = None


class ExecutionTraceView(BaseModel):
    execution_id: UUID
    started_at: datetime
    completed_at: Optional[datetime] = None
    total_latency_ms: Optional[float] = None
    spans: list[SpanView] = []
