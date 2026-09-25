from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import text


class KeywordSearchService:
    def search(self, db: Session, kb_id: int, query: str, top_k: int) -> List[Dict[str, Any]]:
        tsquery = " & ".join(query.split())

        sql_query = text(
            """
            SELECT dc.id, dc.document_id, dc.content, dc.source, dc.page_number,
                   dc.section, dc.created_at, dc.chunk_index,
                   ts_rank(dc.content_tsvector, to_tsquery('english', :tsquery)) AS score
            FROM document_chunks AS dc
            JOIN documents AS d ON dc.document_id = d.id
            WHERE d.knowledge_base_id = :kb_id
              AND d.status = 'completed'
              AND dc.content_tsvector @@ to_tsquery('english', :tsquery)
            ORDER BY score DESC
            LIMIT :top_k
            """
        )

        results = db.execute(
            sql_query,
            {
                "tsquery": tsquery,
                "kb_id": kb_id,
                "top_k": top_k,
            },
        ).fetchall()

        formatted_results = []
        for row in results:
            formatted_results.append(
                {
                    "id": row.id,
                    "document_id": row.document_id,
                    "content": row.content,
                    "source": row.source,
                    "page_number": row.page_number,
                    "section": row.section,
                    "chunk_index": row.chunk_index,
                    "created_at": row.created_at,
                    "score": float(row.score),
                }
            )
        return formatted_results


keyword_search_service = KeywordSearchService()
