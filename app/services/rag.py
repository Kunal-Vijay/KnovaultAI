from typing import List
from sqlalchemy.orm import Session

from app.core.llm import mock_llm_client
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.schemas.rag import RAGRequest, RAGResponse, Citation
from app.schemas.search import SearchResultItem
from app.services.search import semantic_search_service

class Retriever:
    def __init__(self):
        self.semantic_search_service = semantic_search_service

    def retrieve_chunks(self, db: Session, request: RAGRequest) -> List[SearchResultItem]:
        # Reuse the semantic search service to get relevant chunks
        search_results = self.semantic_search_service.search(db, request)
        return search_results

class ContextBuilder:
    def build_context(self, search_results: List[SearchResultItem]) -> str:
        context_parts = []
        for i, item in enumerate(search_results):
            context_parts.append(f"Source {i+1} (Document ID: {item.chunk.document_id}, Chunk ID: {item.chunk.id}):\n{item.chunk.content}")
        return "\n\n".join(context_parts)

class PromptBuilder:
    def build_prompt(self, question: str, context: str) -> str:
        # Construct a prompt for the LLM using the question and context
        prompt = (
            f"Given the following context, answer the question accurately and concisely. "
            f"Cite the sources using 'Source X' as specified in the context.\n\n"
            f"Context:\n{context}\n\n"
            f"Question: {question}\n\n"
            f"Answer:"
        )
        return prompt

class RAGService:
    def __init__(self):
        self.retriever = Retriever()
        self.context_builder = ContextBuilder()
        self.prompt_builder = PromptBuilder()

    def get_answer(self, db: Session, request: RAGRequest) -> RAGResponse:
        # 1. Retrieve relevant chunks
        search_results = self.retriever.retrieve_chunks(db, request)

        # 2. Build context from retrieved chunks
        context = self.context_builder.build_context(search_results)

        # 3. Build prompt for LLM
        prompt = self.prompt_builder.build_prompt(request.question, context)

        # 4. Get response from LLM (using mock client for now)
        llm_answer = mock_llm_client.generate_response(prompt)

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
