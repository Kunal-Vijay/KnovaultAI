class LLMError(Exception):
    """Base LLM gateway error."""


class ModelAuthenticationError(LLMError):
    pass


class ModelRateLimitError(LLMError):
    pass


class ModelTimeoutError(LLMError):
    pass


class ModelUnavailableError(LLMError):
    pass
