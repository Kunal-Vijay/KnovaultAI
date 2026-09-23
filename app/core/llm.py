class MockLLMClient:
    def generate_response(self, prompt: str) -> str:
        # Simple mock LLM. Returns a canned response or echoes part of the prompt.
        if "question" in prompt.lower():
            return "This is a mock answer to your question, based on the provided context. (Source 1)"
        return "Mock LLM response: I received your request and simulated a response. (Source 1)"

mock_llm_client = MockLLMClient()
