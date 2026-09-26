from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import text
import logging

from app.core.embedding import embedding_service
from app.models.document_chunk import DocumentChunk
from app.schemas.search import SearchRequest, SearchResultItem
from app.services.keyword_search import keyword_search_service
from app.utils.rerank import reciprocal_rank_fusion
from app.utils.pgvector import format_pgvector
from app.core.observability import tracer

logger = logging.getLogger(__name__)


class HybridSearchService:
    def __init__(self):
        self.embedding_service = embedding_service
        self.keyword_search_service = keyword_search_service

    def search(self, db: Session, request: SearchRequest) -> List[SearchResultItem]:
        with tracer.start_as_current_span("hybrid_search_service.search") as span:
            span.set_attribute("knowledge_base_id", request.knowledge_base_id)
            span.set_attribute("query", request.query)
            span.set_attribute("keyword_query", request.keyword_query or "")
            span.set_attribute("top_k", request.top_k)
            span.set_attribute("rrf_k", request.rrf_k)

            semantic_ranked_list: list[dict[str, Any]] = []
            with tracer.start_as_current_span("semantic_search"):
                query_embedding = self.embedding_service.embed_text(request.query)
                query_vector = format_pgvector(query_embedding)
                semantic_sql_query = text(
                    """
                    SELECT dc.id, dc.document_id, dc.content, dc.source, dc.page_number,
                           dc.section, dc.created_at, dc.chunk_index,
                           (dc.embedding <=> CAST(:query_embedding AS vector)) AS distance
                    FROM document_chunks AS dc
                    JOIN documents AS d ON dc.document_id = d.id
                    WHERE d.knowledge_base_id = :kb_id
                      AND d.status = 'completed'
                      AND dc.embedding IS NOT NULL
                    ORDER BY distance
                    LIMIT :top_k
                    """
                )
                semantic_results = db.execute(
                    semantic_sql_query,
                    {
                        "query_embedding": query_vector,
                        "kb_id": request.knowledge_base_id,
                        "top_k": request.top_k,
                    },
                ).fetchall()

                for row in semantic_results:
                    similarity = 1.0 - float(row.distance)
                    if (
                        request.similarity_threshold is not None
                        and similarity < request.similarity_threshold
                    ):
                        continue
                    semantic_ranked_list.append(
                        {
                            "id": row.id,
                            "document_id": row.document_id,
                            "content": row.content,
                            "source": row.source,
                            "page_number": row.page_number,
                            "section": row.section,
                            "chunk_index": row.chunk_index,
                            "created_at": row.created_at,
                            "score": similarity,
                        }
                    )
                span.set_attribute("semantic_results_count", len(semantic_ranked_list))
                logger.info("Semantic search returned %s results.", len(semantic_ranked_list))

            keyword_ranked_list: list[dict[str, Any]] = []
            if request.keyword_query:
                with tracer.start_as_current_span("keyword_search"):
                    keyword_results = self.keyword_search_service.search(
                        db,
                        request.knowledge_base_id,
                        request.keyword_query,
                        request.top_k,
                    )
                    keyword_ranked_list = keyword_results
                    span.set_attribute("keyword_results_count", len(keyword_ranked_list))
                    logger.info("Keyword search returned %s results.", len(keyword_ranked_list))

            final_search_results: list[SearchResultItem] = []
            if semantic_ranked_list or keyword_ranked_list:
                with tracer.start_as_current_span("rerank_results_rrf"):
                    all_ranked_lists = []
                    if semantic_ranked_list:
                        all_ranked_lists.append(semantic_ranked_list)
                    if keyword_ranked_list:
                        all_ranked_lists.append(keyword_ranked_list)

                    fused_results = reciprocal_rank_fusion(all_ranked_lists, k=request.rrf_k)

                    semantic_by_id = {
                        item["id"]: float(item["score"])
                        for item in semantic_ranked_list
                    }
                    top_semantic = (
                        max(semantic_by_id.values()) if semantic_by_id else None
                    )
                    top_fusion = (
                        float(fused_results[0].get("fused_score", 0.0))
                        if fused_results
                        else None
                    )
                    if top_semantic is not None:
                        span.set_attribute("top_semantic_similarity", top_semantic)
                    if top_fusion is not None:
                        span.set_attribute("top_fusion_score", top_fusion)

                    for item_data in fused_results:
                        chunk_schema_data = {
                            "id": item_data["id"],
                            "document_id": item_data["document_id"],
                            "content": item_data["content"],
                            "source": item_data.get("source"),
                            "page_number": item_data.get("page_number"),
                            "section": item_data.get("section"),
                            "chunk_index": item_data.get("chunk_index"),
                            "created_at": item_data.get("created_at"),
                        }
                        chunk_id = item_data["id"]
                        chunk = DocumentChunk(**chunk_schema_data)
                        sem = semantic_by_id.get(chunk_id)
                        final_search_results.append(
                            SearchResultItem(
                                chunk=chunk,
                                score=float(item_data.get("fused_score", 0.0)),
                                semantic_score=sem,
                            )
                        )
                    span.set_attribute("reranked_results_count", len(final_search_results))
                    logger.info("Reranking produced %s final results.", len(final_search_results))

            return final_search_results


hybrid_search_service = HybridSearchService()
