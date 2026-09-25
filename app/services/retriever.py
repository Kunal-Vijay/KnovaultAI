from typing import List

from sqlalchemy.orm import Session

from app.schemas.rag import RAGRequest
from app.schemas.search import SearchRequest, SearchResultItem
from app.services.search import hybrid_search_service


class DocumentRetriever:
    """Hybrid retriever scoped to a knowledge base (reference_runtime naming)."""

    def __init__(self):
        self._search = hybrid_search_service

    def retrieve(
        self,
        db: Session,
        *,
        knowledge_base_id: int,
        query: str,
        top_k: int = 5,
        keyword_query: str | None = None,
        similarity_threshold: float | None = None,
    ) -> List[SearchResultItem]:
        request = SearchRequest(
            knowledge_base_id=knowledge_base_id,
            query=query,
            keyword_query=keyword_query or query,
            top_k=top_k,
            similarity_threshold=similarity_threshold,
        )
        return self._search.search(db, request)

    def retrieve_for_rag(self, db: Session, request: RAGRequest) -> List[SearchResultItem]:
        return self.retrieve(
            db,
            knowledge_base_id=request.knowledge_base_id,
            query=request.question,
            top_k=request.top_k,
            keyword_query=request.question,
        )


document_retriever = DocumentRetriever()
