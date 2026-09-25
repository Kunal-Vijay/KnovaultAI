from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class DocumentBase(BaseModel):
    filename: str
    external_storage_ref: str # Reference to external storage (e.g., S3 key)

class DocumentCreate(DocumentBase):
    pass

class Document(DocumentBase):
    id: int
    knowledge_base_id: int
    status: str
    mime_type: Optional[str] = None
    num_pages: Optional[int] = None
    raw_content_size: Optional[int] = None
    content_sha256: Optional[str] = None
    embedding_model: Optional[str] = None
    chunk_count: int = 0
    error_message: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class DocumentUploadRequest(BaseModel):
    filename: str
