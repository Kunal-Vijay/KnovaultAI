from app.schemas.search import SearchResultItem
from app.schemas.document_chunk import DocumentChunk
from datetime import datetime

from app.services.rag_prompts import build_rag_prompt, format_retrieved_context


def _item(content: str, score: float = 0.5) -> SearchResultItem:
    chunk = DocumentChunk(
        id=1,
        document_id=10,
        content=content,
        source="notes.txt",
        created_at=datetime.utcnow(),
    )
    return SearchResultItem(chunk=chunk, score=score)


def test_format_retrieved_context_includes_source():
    text = format_retrieved_context([_item("hello world")])
    assert "notes.txt" in text
    assert "hello world" in text


def test_build_rag_prompt_requires_faithfulness():
    prompt = build_rag_prompt("What is hello?", [_item("hello world")])
    assert "Do not invent facts" in prompt
    assert "What is hello?" in prompt
