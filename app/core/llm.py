from abc import ABC, abstractmethod

class LLMProvider(ABC):
    @abstractmethod
    def generate_response(self, prompt: str) -> str:
        pass

class DummyOpenAIProvider(LLMProvider):
    def generate_response(self, prompt: str) -> str:
        # Simple mock LLM. Returns a canned response or echoes part of the prompt.
        if "question" in prompt.lower():
            return "This is a mock answer from Dummy OpenAI to your question, based on the provided context. (Source 1)"
        return "Mock Dummy OpenAI response: I received your request and simulated a response. (Source 1)"

class LLMGateway:
    def __init__(self, default_provider: LLMProvider):
        self._provider = default_provider
        # In later phases, this will include provider abstraction, model routing, etc.

    def generate_response(self, prompt: str) -> str:
        return self._provider.generate_response(prompt)

# Initialize with a dummy provider for now
llm_gateway = LLMGateway(default_provider=DummyOpenAIProvider())
