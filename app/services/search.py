from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.core.embedding import embedding_service
from app.models.document_chunk import DocumentChunk
from app.schemas.search import SearchRequest, SearchResultItem

class SemanticSearchService:
    def __init__(self):
        self.embedding_service = embedding_service

    def search(self, db: Session, request: SearchRequest) -> List[SearchResultItem]:
        query_embedding = self.embedding_service.embed_text(request.query)

        # Perform vector similarity search
        # Using raw SQL for pgvector operations for clarity and direct control
        # This assumes the 'vector' extension is enabled in PostgreSQL
        sql_query = text(
            """SELECT id, document_id, content, source, page_number, section, created_at, embedding, "
            "embedding <-> :query_embedding AS distance "
            "FROM document_chunks "
            "WHERE knowledge_base_id = :kb_id "
            "ORDER BY distance LIMIT :top_k"""
        )

        # Note: The knowledge_base_id is not directly in document_chunks table
        # It's in the documents table. Need to join or filter based on document.knowledge_base_id
        # For now, will use a placeholder or assume it's directly accessible/denormalized.
        # Let's adjust this to join with documents table.

        sql_query = text(
            """SELECT dc.id, dc.document_id, dc.content, dc.source, dc.page_number, dc.section, dc.created_at, dc.embedding, "
            "dc.embedding <-> :query_embedding AS distance "
            "FROM document_chunks AS dc JOIN documents AS d ON dc.document_id = d.id "
            "WHERE d.knowledge_base_id = :kb_id "
            "ORDER BY distance LIMIT :top_k"""
        )

        results = db.execute(sql_query, {
            "query_embedding": str(query_embedding), # pgvector expects string representation of list
            "kb_id": request.knowledge_base_id,
            "top_k": request.top_k
        }).fetchall()

        search_results = []
        for row in results:
            chunk_data = {
                "id": row.id,
                "document_id": row.document_id,
                "content": row.content,
                "source": row.source,
                "page_number": row.page_number,
                "section": row.section,
                "created_at": row.created_at,
            }
            # Need to convert row to a DocumentChunk Pydantic model. 
            # This might require some more work if we want to include embedding here.
            # For simplicity, we'll map directly to a dict that matches DocumentChunk schema for now.
            # Pydantic's from_attributes=True can handle mapping from SQLAlchemy row objects
            chunk = DocumentChunk(**chunk_data)
            search_results.append(SearchResultItem(chunk=chunk, score=row.distance))
        
        return search_results

semantic_search_service = SemanticSearchService()
