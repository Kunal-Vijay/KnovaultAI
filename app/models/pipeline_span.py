import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from app.db.session import Base


class PipelineSpan(Base):
    __tablename__ = "pipeline_spans"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    execution_id = Column(
        UUID(as_uuid=True),
        ForeignKey("query_executions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    parent_span_id = Column(
        UUID(as_uuid=True),
        ForeignKey("pipeline_spans.id", ondelete="CASCADE"),
        nullable=True,
    )

    name = Column(String(256), nullable=False)
    status = Column(String(32), nullable=False, default="running")
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    ended_at = Column(DateTime, nullable=True)
    latency_ms = Column(Numeric(12, 3), nullable=True)

    model = Column(String(256), nullable=True)
    tokens = Column(JSONB, nullable=True)
    attributes = Column(JSONB, nullable=True)
    input_preview = Column(Text, nullable=True)
    output_preview = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)

    execution = relationship("QueryExecution", back_populates="spans")
    parent = relationship("PipelineSpan", remote_side="PipelineSpan.id")
