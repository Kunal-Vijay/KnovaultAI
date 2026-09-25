from typing import List
from sqlalchemy.orm import Session
import logging

from app.core.llm import llm_gateway
from app.schemas.rag import RAGRequest, RAGResponse, Citation
from app.schemas.search import SearchResultItem
from app.services.retriever import document_retriever
from app.services.rag_prompts import build_rag_prompt
from app.core.observability import tracer

logger = logging.getLogger(__name__)

DEFAULT_CITATION_SCORE_THRESHOLD = 0.01


class RAGService:
    def __init__(self, citation_score_threshold: float = DEFAULT_CITATION_SCORE_THRESHOLD):
        self.retriever = document_retriever
        self.citation_score_threshold = citation_score_threshold

    async def get_answer(self, db: Session, request: RAGRequest) -> RAGResponse:
        with tracer.start_as_current_span("rag_service.get_answer") as span:
            span.set_attribute("knowledge_base_id", request.knowledge_base_id)
            span.set_attribute("question", request.question)

            search_results = self.retriever.retrieve_for_rag(db, request)
            span.set_attribute("retrieval.count", len(search_results))

            prompt = build_rag_prompt(request.question, search_results)

            with tracer.start_as_current_span("llm_gateway.generate_response"):
                llm_result = await llm_gateway.generate_response(prompt)
                logger.info("LLM response generated via %s.", llm_result.model)

            citations = self._build_citations(search_results)
            return RAGResponse(answer=llm_result.response, citations=citations)

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
