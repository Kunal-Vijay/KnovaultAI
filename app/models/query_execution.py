import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from app.db.session import Base


class QueryExecution(Base):
    __tablename__ = "query_executions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    knowledge_base_id = Column(Integer, ForeignKey("knowledge_bases.id"), nullable=False, index=True)

    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=True)
    status = Column(String(32), nullable=False, default="running")

    request_id = Column(String(64), nullable=True)
    otel_trace_id = Column(String(128), nullable=True)

    routed_model = Column(String(256), nullable=True)
    routing_policy = Column(String(64), nullable=True)
    routing_reason = Column(String(512), nullable=True)

    prompt_tokens = Column(Integer, nullable=True)
    completion_tokens = Column(Integer, nullable=True)
    total_tokens = Column(Integer, nullable=True)
    estimated_cost_usd = Column(Numeric(12, 6), nullable=True)

    chunks_retrieved = Column(Integer, nullable=True)
    citations = Column(JSONB, nullable=True)

    latency_ms = Column(Numeric(12, 3), nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    spans = relationship(
        "PipelineSpan",
        back_populates="execution",
        cascade="all, delete-orphan",
        order_by="PipelineSpan.started_at",
    )
