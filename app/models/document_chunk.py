from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector # Import Vector type
from app.db.session import Base

class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    chunk_index = Column(Integer, nullable=True)
    content = Column(Text, nullable=False)
    source = Column(String, nullable=True) # e.g., original filename, URL
    page_number = Column(Integer, nullable=True) # Page number if applicable
    section = Column(String, nullable=True) # Section or heading if applicable
    embedding = Column(Vector(384), nullable=True) # Using 384 dimensions for all-MiniLM-L6-v2
    # content_tsvector is a GENERATED STORED tsvector column in PostgreSQL (managed by migration)
    created_at = Column(DateTime, default=datetime.utcnow)

    document = relationship("Document", back_populates="chunks")

