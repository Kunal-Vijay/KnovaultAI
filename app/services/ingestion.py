import asyncio
import mimetypes
from typing import Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.core.storage import get_storage_client
from app.core.embedding import embedding_service # Import the embedding service
from app.db.session import get_db
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.ingestion.parsers import get_parser
from app.ingestion.chunkers import get_chunker
from app.ingestion.metadata_extractors import get_metadata_extractor

async def ingest_document_background_task(doc_id: int, file_content: bytes):
    db = next(get_db()) # Get a new DB session for the background task
    try:
        document = db.query(Document).filter(Document.id == doc_id).first()
        if not document:
            # Log error: document not found
            return

        # 1. Determine MIME type and get parser
        mime_type = mimetypes.guess_type(document.filename)[0]
        if not mime_type:
            mime_type = "application/octet-stream" # Default if unable to guess

        parser = get_parser(mime_type)
        text_content = parser.parse(file_content)

        # 2. Extract metadata
        metadata_extractor = get_metadata_extractor()
        extracted_metadata = metadata_extractor.extract(file_content, document.filename, mime_type)

        # Update document with extracted metadata
        document.mime_type = mime_type
        document.num_pages = extracted_metadata.get("num_pages")
        document.raw_content_size = len(file_content)
        document.status = "parsing"
        db.add(document)
        db.commit()
        db.refresh(document)

        # 3. Chunk the document
        chunker = get_chunker()
        chunks_content = chunker.chunk(text_content)

        # 4. Create DocumentChunks and generate embeddings
        for i, chunk_content in enumerate(chunks_content):
            embedding = embedding_service.embed_text(chunk_content)
            db_chunk = DocumentChunk(
                document_id=document.id,
                content=chunk_content,
                source=document.filename, # Or a more specific source if available
                page_number=extracted_metadata.get("page_number"),
                section=extracted_metadata.get("section"),
                embedding=embedding
            )
            db.add(db_chunk)
            db.flush() # Flush to get chunk.id for tsvector update

            # Update content_tsvector using raw SQL for PostgreSQL FTS
            db.execute(text("UPDATE document_chunks SET content_tsvector = to_tsvector('english', :content) WHERE id = :chunk_id"),
                       {"content": chunk_content, "chunk_id": db_chunk.id})
        
        document.status = "completed"
        db.add(document)
        db.commit()

    except Exception as e:
        # Log the exception
        if document:
            document.status = "failed"
            db.add(document)
            db.commit()
        print(f"Document ingestion failed for doc_id {doc_id}: {e}")
    finally:
        db.close()

class IngestionService:
    def __init__(self):
        self.storage_client = get_storage_client()

    async def upload_and_ingest_document(self, db: Session, user_id: int, kb_id: int, filename: str, file_content: bytes) -> Document:
        # Save file to external storage (mocked local storage for now)
        storage_ref = self.storage_client.save_file(file_content, filename)

        # Create document entry in DB with 'uploaded' status
        new_document = Document(
            knowledge_base_id=kb_id,
            filename=filename,
            external_storage_ref=storage_ref,
            status="uploaded",
            raw_content_size=len(file_content) # Initial size, might change after parsing
        )
        db.add(new_document)
        db.commit()
        db.refresh(new_document)

        # Trigger background ingestion task (placeholder for now)
        # In a real-world scenario, this would involve a message queue or a proper background task library
        asyncio.create_task(ingest_document_background_task(new_document.id, file_content))

        return new_document

