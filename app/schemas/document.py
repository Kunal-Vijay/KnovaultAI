from pydantic import BaseModel
from datetime import datetime

class DocumentBase(BaseModel):
    filename: str
    external_storage_ref: str

class DocumentCreate(DocumentBase):
    pass

class Document(DocumentBase):
    id: int
    knowledge_base_id: int
    created_at: datetime

    class Config:
        from_attributes = True
