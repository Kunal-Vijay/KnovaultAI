from pydantic import BaseModel, Field


class LLMResponse(BaseModel):
    request_id: str
    model: str
    response: str
    usage: dict = Field(default_factory=dict)
    latency_ms: float = 0.0
    plug_name: str | None = None
    routing_policy: str | None = None
    routing_reason: str | None = None
    estimated_cost_usd: float | None = None
