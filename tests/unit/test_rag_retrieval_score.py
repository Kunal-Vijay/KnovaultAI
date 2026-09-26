from datetime import datetime

from app.schemas.document_chunk import DocumentChunk
from app.schemas.search import SearchResultItem
from app.services.rag import _top_semantic_similarity


def _item(chunk_id: int, fused: float, semantic: float | None) -> SearchResultItem:
    chunk = DocumentChunk(
        id=chunk_id,
        document_id=1,
        content="text",
        chunk_index=0,
        created_at=datetime.utcnow(),
    )
    return SearchResultItem(chunk=chunk, score=fused, semantic_score=semantic)


def test_top_semantic_similarity_max_over_results():
    results = [
        _item(1, fused=0.033, semantic=0.42),
        _item(2, fused=0.016, semantic=0.51),
    ]
    assert _top_semantic_similarity(results) == 0.51


def test_top_semantic_similarity_none_when_keyword_only():
    results = [_item(1, fused=0.016, semantic=None)]
    assert _top_semantic_similarity(results) is None
