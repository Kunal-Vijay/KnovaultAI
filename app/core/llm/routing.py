from __future__ import annotations

from dataclasses import dataclass

from app.core.llm.schemas import LLMResponse


@dataclass(frozen=True, slots=True)
class ModelSelection:
    plug_name: str
    model: str
    fallbacks: tuple[str, ...]
    policy: str
    reason: str


@dataclass(frozen=True, slots=True)
class RoutingContext:
    question: str
    chunks_retrieved: int
    """Best semantic similarity (1 - distance) among retrieved chunks; not RRF fusion score."""
    top_retrieval_score: float | None


class RoutingPolicy:
    """Auto-select model plug from retrieval signals."""

    def __init__(
        self,
        *,
        default_plug: str,
        quality_plug: str,
        fast_plug: str,
        strong_score_threshold: float = 0.35,
        short_question_chars: int = 120,
    ):
        self.default_plug = default_plug
        self.quality_plug = quality_plug
        self.fast_plug = fast_plug
        self.strong_score_threshold = strong_score_threshold
        self.short_question_chars = short_question_chars

    def select(self, context: RoutingContext) -> ModelSelection:
        from app.core.llm.model_plugs import get_model_plug

        if context.chunks_retrieved == 0:
            plug = get_model_plug(self.quality_plug)
            return ModelSelection(
                plug_name=plug.name,
                model=plug.model,
                fallbacks=plug.fallbacks,
                policy="quality",
                reason="No retrieved chunks; using quality model for best-effort answer.",
            )

        similarity = context.top_retrieval_score
        if similarity is None:
            plug = get_model_plug(self.quality_plug)
            return ModelSelection(
                plug_name=plug.name,
                model=plug.model,
                fallbacks=plug.fallbacks,
                policy="quality",
                reason=(
                    "No semantic similarity signal (keyword-only retrieval); using quality model."
                ),
            )

        if similarity < self.strong_score_threshold:
            plug = get_model_plug(self.quality_plug)
            return ModelSelection(
                plug_name=plug.name,
                model=plug.model,
                fallbacks=plug.fallbacks,
                policy="quality",
                reason=(
                    f"Low retrieval confidence (top semantic similarity={similarity:.3f}); "
                    "using quality model."
                ),
            )

        if len(context.question.strip()) <= self.short_question_chars:
            plug = get_model_plug(self.fast_plug)
            return ModelSelection(
                plug_name=plug.name,
                model=plug.model,
                fallbacks=plug.fallbacks,
                policy="fast",
                reason=(
                    f"Short question with strong retrieval (similarity={similarity:.3f}); "
                    "using fast model."
                ),
            )

        plug = get_model_plug(self.default_plug)
        return ModelSelection(
            plug_name=plug.name,
            model=plug.model,
            fallbacks=plug.fallbacks,
            policy="default",
            reason=(
                f"Balanced default routing for standard RAG query (similarity={similarity:.3f})."
            ),
        )
