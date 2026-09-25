import re

from app.core.config import settings

_PARAGRAPH_SPLIT = re.compile(r"\n\s*\n+")


class ParagraphChunker:
    """Split text into paragraph-based chunks (reference_runtime chunk_document style)."""

    def __init__(
        self,
        max_chars: int | None = None,
        chunk_overlap: int | None = None,
    ):
        self.max_chars = max_chars or settings.CHUNK_SIZE
        self.chunk_overlap = chunk_overlap or settings.CHUNK_OVERLAP

    def chunk(self, text: str) -> list[str]:
        cleaned = text.strip()
        if not cleaned:
            return []

        paragraphs = [
            part.strip() for part in _PARAGRAPH_SPLIT.split(cleaned) if part.strip()
        ]
        if not paragraphs:
            paragraphs = [cleaned]

        chunks: list[str] = []
        for paragraph in paragraphs:
            if len(paragraph) <= self.max_chars:
                chunks.append(paragraph)
                continue
            words = paragraph.split()
            i = 0
            while i < len(words):
                piece = words[i : i + self.max_chars]
                chunks.append(" ".join(piece))
                step = max(1, self.max_chars - self.chunk_overlap)
                i += step

        return chunks


def get_chunker() -> ParagraphChunker:
    return ParagraphChunker()
