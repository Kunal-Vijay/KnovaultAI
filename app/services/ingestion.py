import asyncio
import mimetypes
import logging
from typing import Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.core.storage import get_storage_client
from app.core.embedding import embedding_service
from app.db.session import get_db
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.ingestion.parsers import get_parser
from app.ingestion.chunkers import get_chunker
from app.ingestion.metadata_extractors import get_metadata_extractor
from app.core.observability import tracer # Import tracer

logger = logging.getLogger(__name__)

async def ingest_document_background_task(doc_id: int, file_content: bytes):
    with tracer.start_as_current_span("ingest_document_background_task") as span:
        span.set_attribute("document_id", doc_id)
        db = next(get_db()) # Get a new DB session for the background task
        document = None # Initialize document to None
        try:
            document = db.query(Document).filter(Document.id == doc_id).first()
            if not document:
                logger.error(f"Document not found for ingestion: {doc_id}")
                span.set_attribute("error", True)
                span.record_exception(ValueError(f"Document not found: {doc_id}"))
                return

            logger.info(f"Starting ingestion for document: {document.filename} (ID: {doc_id})")
            span.set_attribute("document.filename", document.filename)

            # 1. Determine MIME type and get parser
            with tracer.start_as_current_span("parse_document"):
                mime_type = mimetypes.guess_type(document.filename)[0]
                if not mime_type:
                    mime_type = "application/octet-stream" # Default if unable to guess
                span.set_attribute("document.mime_type", mime_type)

                parser = get_parser(mime_type)
                text_content = parser.parse(file_content)

            # 2. Extract metadata
            with tracer.start_as_current_span("extract_metadata"):
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
            logger.info(f"Document {doc_id} parsed and metadata extracted.")

            # 3. Chunk the document
            with tracer.start_as_current_span("chunk_document"):
                chunker = get_chunker()
                chunks_content = chunker.chunk(text_content)
                span.set_attribute("document.chunks_count", len(chunks_content))
                logger.info(f"Document {doc_id} chunked into {len(chunks_content)} chunks.")

            # 4. Create DocumentChunks and generate embeddings
            with tracer.start_as_current_span("create_chunks_and_embed"):
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
                db.commit()
                logger.info(f"Document {doc_id} chunks created and embeddings generated.")
            
            document.status = "completed"
            db.add(document)
            db.commit()
            logger.info(f"Document {doc_id} ingestion completed successfully.")

        except Exception as e:
            logger.exception(f"Document ingestion failed for doc_id {doc_id}")
            if document:
                document.status = "failed"
                db.add(document)
                db.commit()
            span.set_attribute("error", True)
            span.record_exception(e)
        finally:
            db.close()

class IngestionService:
    def __init__(self):
        self.storage_client = get_storage_client()

    async def upload_and_ingest_document(self, db: Session, user_id: int, kb_id: int, filename: str, file_content: bytes) -> Document:
        with tracer.start_as_current_span("upload_and_ingest_document") as span:
            span.set_attribute("user_id", user_id)
            span.set_attribute("kb_id", kb_id)
            span.set_attribute("filename", filename)

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
            span.set_attribute("document_id", new_document.id)
            logger.info(f"Document {new_document.id} uploaded and awaiting ingestion.")

            # Trigger background ingestion task (placeholder for now)
            # In a real-world scenario, this would involve a message queue or a proper background task library
            asyncio.create_task(ingest_document_background_task(new_document.id, file_content))

            return new_document

