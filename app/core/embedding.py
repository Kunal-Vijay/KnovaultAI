from typing import TYPE_CHECKING

from app.core.config import settings

if TYPE_CHECKING:
    from sentence_transformers import SentenceTransformer


class EmbeddingService:
    def __init__(self):
        self._model: SentenceTransformer | None = None

    @property
    def model_name(self) -> str:
        return settings.EMBEDDING_MODEL

    def _get_model(self) -> SentenceTransformer:
        if self._model is None:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(settings.EMBEDDING_MODEL)
        return self._model

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        vectors = self._get_model().encode(
            texts,
            normalize_embeddings=True,
            convert_to_numpy=True,
        )
        return [vector.tolist() for vector in vectors]

    def embed_text(self, text: str) -> list[float]:
        return self.embed_batch([text])[0]


embedding_service = EmbeddingService()
