from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.core.embedding import embedding_service
from app.models.document_chunk import DocumentChunk
from app.schemas.search import SearchRequest, SearchResultItem
from app.services.keyword_search import keyword_search_service
from app.utils.rerank import reciprocal_rank_fusion

class HybridSearchService:
    def __init__(self):
        self.embedding_service = embedding_service
        self.keyword_search_service = keyword_search_service

    def search(self, db: Session, request: SearchRequest) -> List[SearchResultItem]:
        # 1. Perform Semantic Search
        query_embedding = self.embedding_service.embed_text(request.query)
        semantic_sql_query = text(
            """SELECT dc.id, dc.document_id, dc.content, dc.source, dc.page_number, dc.section, dc.created_at, dc.embedding, "
            "(dc.embedding <-> :query_embedding) AS distance "
            "FROM document_chunks AS dc JOIN documents AS d ON dc.document_id = d.id "
            "WHERE d.knowledge_base_id = :kb_id "
            "ORDER BY distance LIMIT :top_k"""
        )
        semantic_results = db.execute(semantic_sql_query, {
            "query_embedding": str(query_embedding),
            "kb_id": request.knowledge_base_id,
            "top_k": request.top_k
        }).fetchall()

        semantic_ranked_list = []
        for row in semantic_results:
            # Need to ensure that the dictionary has all the keys that DocumentChunk expects.
            # And also include the score for RRF.
            semantic_ranked_list.append({
                "id": row.id,
                "document_id": row.document_id,
                "content": row.content,
                "source": row.source,
                "page_number": row.page_number,
                "section": row.section,
                "created_at": row.created_at,
                "score": 1 - row.distance, # Convert distance (lower is better) to similarity (higher is better)
            })

        # 2. Perform Keyword Search (if keyword_query is provided)
        keyword_ranked_list = []
        if request.keyword_query:
            keyword_results = self.keyword_search_service.search(db, request.knowledge_base_id, request.keyword_query, request.top_k)
            keyword_ranked_list = keyword_results

        # 3. Combine and Rerank using RRF
        all_ranked_lists = []
        if semantic_ranked_list: all_ranked_lists.append(semantic_ranked_list)
        if keyword_ranked_list: all_ranked_lists.append(keyword_ranked_list)

        if not all_ranked_lists: # No results from either search
            return []
        
        fused_results = reciprocal_rank_fusion(all_ranked_lists, k=request.rrf_k)

        # 4. Map fused results back to SearchResultItem schema
        final_search_results = []
        for item_data in fused_results:
            # Ensure the item_data is suitable for DocumentChunk schema
            # Remove 'score' and 'fused_score' before passing to DocumentChunk if not part of schema
            # We can retrieve the full chunk object from the database if needed, or pass the dict.
            chunk_schema_data = {
                "id": item_data['id'],
                "document_id": item_data['document_id'],
                "content": item_data['content'],
                "source": item_data.get('source'),
                "page_number": item_data.get('page_number'),
                "section": item_data.get('section'),
                "created_at": item_data.get('created_at'),
            }
            chunk = DocumentChunk(**chunk_schema_data)
            # Use fused_score as the score for the final SearchResultItem
            final_search_results.append(SearchResultItem(chunk=chunk, score=item_data.get('fused_score', 0.0)))

        return final_search_results

hybrid_search_service = HybridSearchService()
