from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import text
import logging

from app.core.embedding import embedding_service
from app.models.document_chunk import DocumentChunk
from app.schemas.search import SearchRequest, SearchResultItem
from app.services.keyword_search import keyword_search_service
from app.utils.rerank import reciprocal_rank_fusion
from app.core.observability import tracer # Import tracer

logger = logging.getLogger(__name__)

class HybridSearchService:
    def __init__(self):
        self.embedding_service = embedding_service
        self.keyword_search_service = keyword_search_service

    def search(self, db: Session, request: SearchRequest) -> List[SearchResultItem]:
        with tracer.start_as_current_span("hybrid_search_service.search") as span:
            span.set_attribute("knowledge_base_id", request.knowledge_base_id)
            span.set_attribute("query", request.query)
            span.set_attribute("keyword_query", request.keyword_query)
            span.set_attribute("top_k", request.top_k)
            span.set_attribute("rrf_k", request.rrf_k)

            # 1. Perform Semantic Search
            semantic_ranked_list = []
            with tracer.start_as_current_span("semantic_search"):
                query_embedding = self.embedding_service.embed_text(request.query)
                semantic_sql_query = text(
                    """SELECT dc.id, dc.document_id, dc.content, dc.source, dc.page_number, dc.section, dc.created_at, dc.embedding,
                    (dc.embedding <-> :query_embedding) AS distance
                    FROM document_chunks AS dc JOIN documents AS d ON dc.document_id = d.id
                    WHERE d.knowledge_base_id = :kb_id
                    ORDER BY distance LIMIT :top_k"""
                )
                semantic_results = db.execute(semantic_sql_query, {
                    "query_embedding": str(query_embedding),
                    "kb_id": request.knowledge_base_id,
                    "top_k": request.top_k
                }).fetchall()

                for row in semantic_results:
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
                span.set_attribute("semantic_results_count", len(semantic_ranked_list))
                logger.info(f"Semantic search returned {len(semantic_ranked_list)} results.")

            # 2. Perform Keyword Search (if keyword_query is provided)
            keyword_ranked_list = []
            if request.keyword_query:
                with tracer.start_as_current_span("keyword_search"):
                    keyword_results = self.keyword_search_service.search(db, request.knowledge_base_id, request.keyword_query, request.top_k)
                    keyword_ranked_list = keyword_results
                    span.set_attribute("keyword_results_count", len(keyword_ranked_list))
                    logger.info(f"Keyword search returned {len(keyword_ranked_list)} results.")

            # 3. Combine and Rerank using RRF
            final_search_results = []
            if semantic_ranked_list or keyword_ranked_list:
                with tracer.start_as_current_span("rerank_results_rrf"):
                    all_ranked_lists = []
                    if semantic_ranked_list: all_ranked_lists.append(semantic_ranked_list)
                    if keyword_ranked_list: all_ranked_lists.append(keyword_ranked_list)

                    fused_results = reciprocal_rank_fusion(all_ranked_lists, k=request.rrf_k)

                    # 4. Map fused results back to SearchResultItem schema
                    for item_data in fused_results:
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
                        final_search_results.append(SearchResultItem(chunk=chunk, score=item_data.get('fused_score', 0.0)))
                    span.set_attribute("reranked_results_count", len(final_search_results))
                    logger.info(f"Reranking produced {len(final_search_results)} final results.")
            
            return final_search_results

hybrid_search_service = HybridSearchService()
