from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import text

class KeywordSearchService:
    def search(self, db: Session, kb_id: int, query: str, top_k: int) -> List[Dict[str, Any]]:
        # Convert natural language query to tsquery
        tsquery = " & ".join(query.split())

        # Perform keyword search using PostgreSQL FTS
        sql_query = text(
            """SELECT dc.id, dc.document_id, dc.content, dc.source, dc.page_number, dc.section, dc.created_at,
            ts_rank(to_tsvector('english', dc.content), to_tsquery('english', :tsquery)) AS score
            FROM document_chunks AS dc JOIN documents AS d ON dc.document_id = d.id
            WHERE d.knowledge_base_id = :kb_id
              AND to_tsvector('english', dc.content) @@ to_tsquery('english', :tsquery)
            ORDER BY score DESC LIMIT :top_k"""
        )

        results = db.execute(sql_query, {
            "tsquery": tsquery,
            "kb_id": kb_id,
            "top_k": top_k
        }).fetchall()

        # Format results to be similar to semantic search results for RRF compatibility
        formatted_results = []
        for row in results:
            formatted_results.append({
                "id": row.id,
                "document_id": row.document_id,
                "content": row.content,
                "source": row.source,
                "page_number": row.page_number,
                "section": row.section,
                "created_at": row.created_at,
                "score": row.score # Keyword search score
            })
        return formatted_results

keyword_search_service = KeywordSearchService()
