from pydantic import BaseModel
from typing import List, Optional

from app.schemas.document_chunk import DocumentChunk

class SearchRequest(BaseModel):
    knowledge_base_id: int
    query: str
    keyword_query: Optional[str] = None # New: for keyword search
    top_k: int = 5
    rrf_k: int = 60 # New: K parameter for Reciprocal Rank Fusion

class SearchResultItem(BaseModel):
    chunk: DocumentChunk
    score: float

class SearchResponse(BaseModel):
    results: List[SearchResultItem]
