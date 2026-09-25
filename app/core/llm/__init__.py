from abc import ABC, abstractmethod

from app.core.config import settings
from app.core.llm.errors import LLMError
from app.core.llm.openrouter import OpenRouterProvider
from app.core.llm.schemas import LLMResponse

__all__ = [
    "LLMProvider",
    "DummyOpenAIProvider",
    "LLMGateway",
    "create_llm_gateway",
    "llm_gateway",
    "LLMResponse",
]


class LLMProvider(ABC):
    @abstractmethod
    async def generate(self, prompt: str) -> LLMResponse:
        pass


class DummyOpenAIProvider(LLMProvider):
    async def generate(self, prompt: str) -> LLMResponse:
        return LLMResponse(
            request_id="dummy",
            model="dummy",
            response=(
                "This is a mock answer from Dummy OpenAI to your question, "
                "based on the provided context. (Source 1)"
            ),
        )


class LLMGateway:
    def __init__(self, default_provider: LLMProvider):
        self._provider = default_provider

    async def generate_response(self, prompt: str) -> LLMResponse:
        return await self._provider.generate(prompt)


def create_llm_gateway() -> LLMGateway:
    if settings.DEFAULT_LLM_PROVIDER == "openrouter":
        return LLMGateway(OpenRouterProvider())
    if settings.DEFAULT_LLM_PROVIDER == "openai_dummy":
        return LLMGateway(DummyOpenAIProvider())
    raise LLMError(f"Unsupported DEFAULT_LLM_PROVIDER: {settings.DEFAULT_LLM_PROVIDER}")


llm_gateway = create_llm_gateway()
