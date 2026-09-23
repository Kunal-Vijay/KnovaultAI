from pydantic import BaseModel
from datetime import datetime

class DocumentChunkBase(BaseModel):
    content: str

class DocumentChunkCreate(DocumentChunkBase):
    pass

class DocumentChunk(DocumentChunkBase):
    id: int
    document_id: int
    created_at: datetime

    class Config:
        from_attributes = True
