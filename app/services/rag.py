import time
from typing import List

from opentelemetry import trace
from sqlalchemy.orm import Session
import logging

from app.core.llm import RoutingContext, llm_gateway
from app.observability.pipeline_tracer import PipelineRecorder
from app.schemas.rag import Citation, RAGRequest, RAGResponse, TokenUsage
from app.schemas.search import SearchResultItem
from app.services.query_execution_store import query_execution_store
from app.services.retriever import document_retriever
from app.services.rag_prompts import build_rag_prompt
from app.core.observability import tracer

DEFAULT_CITATION_SCORE_THRESHOLD = 0.01


def _top_semantic_similarity(search_results: List[SearchResultItem]) -> float | None:
    scores = [r.semantic_score for r in search_results if r.semantic_score is not None]
    return max(scores) if scores else None


class RAGService:
    def __init__(self, citation_score_threshold: float = DEFAULT_CITATION_SCORE_THRESHOLD):
        self.retriever = document_retriever
        self.citation_score_threshold = citation_score_threshold

    async def get_answer(
        self,
        db: Session,
        request: RAGRequest,
        *,
        user_id: int,
        request_id: str | None = None,
    ) -> RAGResponse:
        start = time.perf_counter()
        otel_span = trace.get_current_span()
        otel_trace_id = None
        if otel_span:
            ctx = otel_span.get_span_context()
            if ctx.trace_id:
                otel_trace_id = format(ctx.trace_id, "032x")

        execution = query_execution_store.create_execution(
            db,
            user_id=user_id,
            knowledge_base_id=request.knowledge_base_id,
            question=request.question,
            request_id=request_id,
            otel_trace_id=otel_trace_id,
        )
        recorder = PipelineRecorder(db, execution.id)

        with tracer.start_as_current_span("rag_service.get_answer") as span:
            span.set_attribute("knowledge_base_id", request.knowledge_base_id)
            span.set_attribute("execution_id", str(execution.id))

            try:
                with recorder.span(
                    "rag_service.get_answer",
                    input_preview=request.question,
                    attributes={"knowledge_base_id": request.knowledge_base_id},
                ) as root_span:
                    search_results: List[SearchResultItem] = []
                    with recorder.span(
                        "hybrid_search_service.search",
                        input_preview=request.question,
                    ) as search_span:
                        search_results = self.retriever.retrieve_for_rag(db, request)
                        top_semantic = _top_semantic_similarity(search_results)
                        top_fusion = search_results[0].score if search_results else None
                        search_attrs: dict = {
                            "semantic_results_count": len(search_results),
                            "top_fusion_score": top_fusion,
                        }
                        if top_semantic is not None:
                            search_attrs["top_semantic_similarity"] = top_semantic
                            search_attrs["top_score"] = top_semantic
                        recorder.complete_span(
                            search_span,
                            attributes=search_attrs,
                            output_preview=f"{len(search_results)} chunks retrieved",
                        )

                    prompt = build_rag_prompt(request.question, search_results)
                    routing_context = RoutingContext(
                        question=request.question,
                        chunks_retrieved=len(search_results),
                        top_retrieval_score=_top_semantic_similarity(search_results),
                    )

                    with recorder.span(
                        "llm_gateway.generate_response",
                        input_preview=prompt,
                    ) as llm_span:
                        llm_result = await llm_gateway.generate_response(
                            prompt,
                            routing_context=routing_context,
                        )
                        recorder.complete_span(
                            llm_span,
                            model=llm_result.model,
                            tokens=llm_result.usage,
                            output_preview=llm_result.response,
                            attributes={
                                "plug_name": llm_result.plug_name,
                                "routing_policy": llm_result.routing_policy,
                                "routing_reason": llm_result.routing_reason,
                            },
                        )

                    citations = self._build_citations(search_results)
                    latency_ms = (time.perf_counter() - start) * 1000
                    usage = llm_result.usage or {}
                    prompt_t = usage.get("prompt_tokens")
                    completion_t = usage.get("completion_tokens")
                    total_t = usage.get("total_tokens")

                    query_execution_store.finalize_execution(
                        db,
                        execution,
                        status="completed",
                        answer=llm_result.response,
                        citations=[c.model_dump() for c in citations],
                        chunks_retrieved=len(search_results),
                        routed_model=llm_result.model,
                        routing_policy=llm_result.routing_policy,
                        routing_reason=llm_result.routing_reason,
                        prompt_tokens=int(prompt_t) if prompt_t is not None else None,
                        completion_tokens=int(completion_t) if completion_t is not None else None,
                        total_tokens=int(total_t) if total_t is not None else None,
                        estimated_cost_usd=llm_result.estimated_cost_usd,
                        latency_ms=latency_ms,
                    )
                    recorder.complete_span(
                        root_span,
                        output_preview=llm_result.response,
                        model=llm_result.model,
                        tokens=llm_result.usage,
                    )

                    return RAGResponse(
                        answer=llm_result.response,
                        citations=citations,
                        execution_id=execution.id,
                        routed_model=llm_result.model,
                        routing_policy=llm_result.routing_policy,
                        routing_reason=llm_result.routing_reason,
                        usage=TokenUsage(
                            prompt_tokens=int(prompt_t) if prompt_t is not None else None,
                            completion_tokens=int(completion_t) if completion_t is not None else None,
                            total_tokens=int(total_t) if total_t is not None else None,
                        ),
                        estimated_cost_usd=llm_result.estimated_cost_usd,
                        latency_ms=latency_ms,
                    )
            except Exception as exc:
                latency_ms = (time.perf_counter() - start) * 1000
                query_execution_store.finalize_execution(
                    db,
                    execution,
                    status="failed",
                    error_message=str(exc),
                    latency_ms=latency_ms,
                )
                raise

    def _build_citations(self, search_results: List[SearchResultItem]) -> list[Citation]:
        citations: list[Citation] = []
        for item in search_results:
            if item.score < self.citation_score_threshold:
                continue
            citations.append(
                Citation(
                    document_id=item.chunk.document_id,
                    chunk_id=item.chunk.id,
                    source=item.chunk.source,
                    page_number=item.chunk.page_number,
                    section=item.chunk.section,
                )
            )
        return citations


rag_service = RAGService()
