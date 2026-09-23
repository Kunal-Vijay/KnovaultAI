from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class DocumentChunkBase(BaseModel):
    content: str
    source: Optional[str] = None
    page_number: Optional[int] = None
    section: Optional[str] = None

class DocumentChunkCreate(DocumentChunkBase):
    pass

class DocumentChunk(DocumentChunkBase):
    id: int
    document_id: int
    created_at: datetime

    class Config:
        from_attributes = True
