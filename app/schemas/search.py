from pydantic import BaseModel
from typing import List, Optional

from app.schemas.document_chunk import DocumentChunk

class SearchRequest(BaseModel):
    knowledge_base_id: int
    query: str
    top_k: int = 5

class SearchResultItem(BaseModel):
    chunk: DocumentChunk
    score: float

class SearchResponse(BaseModel):
    results: List[SearchResultItem]
