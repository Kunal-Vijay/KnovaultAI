from typing import Protocol


class DocumentParser(Protocol):
    def parse(self, file_content: bytes) -> str: ...


class Chunker(Protocol):
    def chunk(self, text: str) -> list[str]: ...


class EmbeddingProvider(Protocol):
    @property
    def model_name(self) -> str: ...

    def embed_batch(self, texts: list[str]) -> list[list[float]]: ...

    def embed_text(self, text: str) -> list[float]: ...
