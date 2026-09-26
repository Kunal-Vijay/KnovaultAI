from abc import ABC, abstractmethod

from app.core.config import settings
from app.core.llm.errors import LLMError
from app.core.llm.openrouter import OpenRouterProvider
from app.core.llm.pricing import estimate_cost_usd
from app.core.llm.routing import ModelSelection, RoutingContext, RoutingPolicy
from app.core.llm.schemas import LLMResponse

__all__ = [
    "LLMProvider",
    "DummyOpenAIProvider",
    "LLMGateway",
    "RoutingLLMGateway",
    "create_llm_gateway",
    "llm_gateway",
    "LLMResponse",
    "RoutingContext",
    "ModelSelection",
]


class LLMProvider(ABC):
    @abstractmethod
    async def generate(self, prompt: str, *, selection: ModelSelection | None = None) -> LLMResponse:
        pass


class DummyOpenAIProvider(LLMProvider):
    async def generate(self, prompt: str, *, selection: ModelSelection | None = None) -> LLMResponse:
        return LLMResponse(
            request_id="dummy",
            model="dummy",
            response=(
                "This is a mock answer from Dummy OpenAI to your question, "
                "based on the provided context. (Source 1)"
            ),
            plug_name=selection.plug_name if selection else None,
            routing_policy=selection.policy if selection else None,
            routing_reason=selection.reason if selection else None,
            estimated_cost_usd=0.0,
        )


class RoutingLLMGateway:
    def __init__(self):
        self._policy = RoutingPolicy(
            default_plug=settings.LLM_ROUTING_DEFAULT_PLUG,
            quality_plug=settings.LLM_ROUTING_QUALITY_PLUG,
            fast_plug=settings.LLM_ROUTING_FAST_PLUG,
            strong_score_threshold=settings.LLM_ROUTING_STRONG_SIMILARITY_THRESHOLD,
        )

    def route(self, context: RoutingContext) -> ModelSelection:
        selection = self._policy.select(context)
        if settings.OPENROUTER_MODEL.strip():
            return ModelSelection(
                plug_name=selection.plug_name,
                model=settings.OPENROUTER_MODEL.strip(),
                fallbacks=selection.fallbacks,
                policy=selection.policy,
                reason=f"{selection.reason} (primary overridden by OPENROUTER_MODEL)",
            )
        return selection

    async def generate_response(
        self,
        prompt: str,
        *,
        routing_context: RoutingContext,
    ) -> LLMResponse:
        selection = self.route(routing_context)
        provider = OpenRouterProvider(
            model=selection.model,
            fallbacks=selection.fallbacks,
        )
        raw = await provider.generate(prompt)
        cost = estimate_cost_usd(raw.model, raw.usage)
        return LLMResponse(
            request_id=raw.request_id,
            model=raw.model,
            response=raw.response,
            usage=raw.usage,
            latency_ms=raw.latency_ms,
            plug_name=selection.plug_name,
            routing_policy=selection.policy,
            routing_reason=selection.reason,
            estimated_cost_usd=cost,
        )


class LLMGateway:
    """Backward-compatible wrapper."""

    def __init__(self, inner: RoutingLLMGateway):
        self._inner = inner

    async def generate_response(
        self,
        prompt: str,
        *,
        routing_context: RoutingContext | None = None,
    ) -> LLMResponse:
        ctx = routing_context or RoutingContext(
            question=prompt[:200],
            chunks_retrieved=1,
            top_retrieval_score=0.5,
        )
        return await self._inner.generate_response(prompt, routing_context=ctx)


class _DummyGateway:
    async def generate_response(
        self,
        prompt: str,
        *,
        routing_context: RoutingContext | None = None,
    ) -> LLMResponse:
        return LLMResponse(
            request_id="dummy",
            model="dummy",
            response="Mock answer based on provided context.",
            plug_name="dummy",
            routing_policy="dummy",
            routing_reason="Dummy provider",
            estimated_cost_usd=0.0,
        )


def create_llm_gateway() -> LLMGateway | _DummyGateway:
    if settings.DEFAULT_LLM_PROVIDER == "openai_dummy":
        return _DummyGateway()
    if settings.DEFAULT_LLM_PROVIDER == "openrouter":
        return LLMGateway(RoutingLLMGateway())
    raise LLMError(f"Unsupported DEFAULT_LLM_PROVIDER: {settings.DEFAULT_LLM_PROVIDER}")


llm_gateway = create_llm_gateway()
