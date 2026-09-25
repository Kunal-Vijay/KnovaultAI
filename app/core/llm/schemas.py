from pydantic import BaseModel, Field


class LLMResponse(BaseModel):
    request_id: str
    model: str
    response: str
    usage: dict = Field(default_factory=dict)
    latency_ms: float = 0.0
