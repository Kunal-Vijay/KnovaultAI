from contextlib import contextmanager
from typing import Any, Generator
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.pipeline_span import PipelineSpan
from app.services.query_execution_store import query_execution_store


class PipelineRecorder:
    """Persist nested pipeline spans for one query execution."""

    def __init__(self, db: Session, execution_id: UUID):
        self.db = db
        self.execution_id = execution_id
        self._stack: list[PipelineSpan] = []

    @contextmanager
    def span(
        self,
        name: str,
        *,
        attributes: dict[str, Any] | None = None,
        input_preview: str | None = None,
    ) -> Generator[PipelineSpan, None, None]:
        parent = self._stack[-1] if self._stack else None
        row = query_execution_store.start_span(
            self.db,
            execution_id=self.execution_id,
            name=name,
            parent_span_id=parent.id if parent else None,
            attributes=attributes,
            input_preview=input_preview,
        )
        self._stack.append(row)
        try:
            yield row
        except Exception as exc:
            query_execution_store.complete_span(
                self.db,
                row,
                status="failed",
                error_message=str(exc),
            )
            raise
        finally:
            self._stack.pop()

    def complete_span(
        self,
        span: PipelineSpan,
        *,
        status: str = "completed",
        output_preview: str | None = None,
        model: str | None = None,
        tokens: dict[str, Any] | None = None,
        attributes: dict[str, Any] | None = None,
        error_message: str | None = None,
    ) -> None:
        query_execution_store.complete_span(
            self.db,
            span,
            status=status,
            output_preview=output_preview,
            model=model,
            tokens=tokens,
            attributes=attributes,
            error_message=error_message,
        )
