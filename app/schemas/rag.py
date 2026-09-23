from pydantic import BaseModel
from typing import List, Optional

class RAGRequest(BaseModel):
    knowledge_base_id: int
    question: str
    top_k: int = 5 # Number of chunks to retrieve for context

class Citation(BaseModel):
    document_id: int
    chunk_id: int
    source: Optional[str] = None
    page_number: Optional[int] = None
    section: Optional[str] = None

class RAGResponse(BaseModel):
    answer: str
    citations: List[Citation]
