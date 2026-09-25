from app.ingestion.chunkers import ParagraphChunker


def test_paragraph_chunker_splits_blank_lines():
    chunker = ParagraphChunker(max_chars=200, chunk_overlap=20)
    text = "First paragraph.\n\nSecond paragraph."
    chunks = chunker.chunk(text)
    assert len(chunks) == 2
    assert "First" in chunks[0]
    assert "Second" in chunks[1]


def test_paragraph_chunker_empty():
    assert ParagraphChunker().chunk("   ") == []
