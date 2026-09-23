from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.db.session import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    knowledge_base_id = Column(Integer, ForeignKey("knowledge_bases.id"), nullable=False)
    filename = Column(String, nullable=False)
    external_storage_ref = Column(String, nullable=False) # Reference to external storage (e.g., S3 key)
    status = Column(String, default="uploaded", nullable=False) # e.g., uploaded, parsing, chunking, completed, failed
    mime_type = Column(String, nullable=True)
    num_pages = Column(Integer, nullable=True) # For document types that have pages
    raw_content_size = Column(Integer, nullable=True) # Size in bytes of the raw content
    created_at = Column(DateTime, default=datetime.utcnow)

    knowledge_base = relationship("KnowledgeBase", back_populates="documents")
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")

