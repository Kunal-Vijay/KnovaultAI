from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from uuid import UUID


class RAGRequest(BaseModel):
    knowledge_base_id: int
    question: str
    top_k: int = 5


class Citation(BaseModel):
    document_id: int
    chunk_id: int
    source: Optional[str] = None
    page_number: Optional[int] = None
    section: Optional[str] = None


class TokenUsage(BaseModel):
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None


class RAGResponse(BaseModel):
    answer: str
    citations: List[Citation]
    execution_id: Optional[UUID] = None
    routed_model: Optional[str] = None
    routing_policy: Optional[str] = None
    routing_reason: Optional[str] = None
    usage: Optional[TokenUsage] = None
    estimated_cost_usd: Optional[float] = None
    latency_ms: Optional[float] = None
