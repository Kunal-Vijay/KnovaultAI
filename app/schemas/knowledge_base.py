from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class KnowledgeBaseBase(BaseModel):
    name: str
    description: Optional[str] = None

class KnowledgeBaseCreate(KnowledgeBaseBase):
    pass

class KnowledgeBase(KnowledgeBaseBase):
    id: int
    owner_id: int
    created_at: datetime

    class Config:
        from_attributes = True
