from typing import List
from sqlalchemy.orm import Session
import logging

from app.core.llm import llm_gateway # Import the LLM gateway
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.schemas.rag import RAGRequest, RAGResponse, Citation
from app.schemas.search import SearchResultItem
from app.services.search import hybrid_search_service # Use the hybrid search service
from app.core.observability import tracer # Import tracer

logger = logging.getLogger(__name__)

class Retriever:
    def __init__(self):
        self.hybrid_search_service = hybrid_search_service

    def retrieve_chunks(self, db: Session, request: RAGRequest) -> List[SearchResultItem]:
        with tracer.start_as_current_span("rag_retriever.retrieve_chunks"):
            # Use the hybrid search service to get relevant chunks
            search_results = self.hybrid_search_service.search(db, request)
            logger.info(f"Retrieved {len(search_results)} chunks for RAG request.")
            return search_results

class ContextBuilder:
    def build_context(self, search_results: List[SearchResultItem]) -> str:
        with tracer.start_as_current_span("rag_context_builder.build_context"):
            context_parts = []
            for i, item in enumerate(search_results):
                context_parts.append(f"Source {i+1} (Document ID: {item.chunk.document_id}, Chunk ID: {item.chunk.id}):\n{item.chunk.content}")
            context = "\n\n".join(context_parts)
            logger.debug(f"Context built: {context[:200]}...") # Log first 200 chars
            return context

class PromptBuilder:
    def build_prompt(self, question: str, context: str) -> str:
        with tracer.start_as_current_span("rag_prompt_builder.build_prompt"):
            # Construct a prompt for the LLM using the question and context
            prompt = (
                f"Given the following context, answer the question accurately and concisely. "
                f"Cite the sources using 'Source X' as specified in the context.\n\n"
                f"Context:\n{context}\n\n"
                f"Question: {question}\n\n"
                f"Answer:"
            )
            logger.debug(f"Prompt built: {prompt[:200]}...") # Log first 200 chars
            return prompt

class RAGService:
    def __init__(self):
        self.retriever = Retriever()
        self.context_builder = ContextBuilder()
        self.prompt_builder = PromptBuilder()

    def get_answer(self, db: Session, request: RAGRequest) -> RAGResponse:
        with tracer.start_as_current_span("rag_service.get_answer") as span:
            span.set_attribute("knowledge_base_id", request.knowledge_base_id)
            span.set_attribute("question", request.question)

            # 1. Retrieve relevant chunks
            search_results = self.retriever.retrieve_chunks(db, request)

            # 2. Build context from retrieved chunks
            context = self.context_builder.build_context(search_results)

            # 3. Build prompt for LLM
            prompt = self.prompt_builder.build_prompt(request.question, context)

            # 4. Get response from LLM (using LLM Gateway)
            with tracer.start_as_current_span("llm_gateway.generate_response"):
                llm_answer = llm_gateway.generate_response(prompt)
                logger.info("LLM response generated.")

            # 5. Extract citations (simple placeholder for now)
            citations = []
            for i, item in enumerate(search_results):
                citations.append(Citation(
                    document_id=item.chunk.document_id,
                    chunk_id=item.chunk.id,
                    source=item.chunk.source, # Using chunk source as citation
                    page_number=item.chunk.page_number,
                    section=item.chunk.section
                ))

            return RAGResponse(answer=llm_answer, citations=citations)

rag_service = RAGService()
