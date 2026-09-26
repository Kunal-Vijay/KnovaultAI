import asyncio
import hashlib
import logging
import mimetypes
import uuid
from concurrent.futures import ThreadPoolExecutor

from sqlalchemy.orm import Session

from app.core.embedding import embedding_service
from app.core.observability import tracer
from app.core.storage import build_document_object_key, get_storage_client
from app.db.session import SessionLocal
from app.ingestion.chunkers import get_chunker
from app.ingestion.metadata_extractors import get_metadata_extractor
from app.ingestion.parsers import get_parser
from app.models.document import Document
from app.models.document_chunk import DocumentChunk

logger = logging.getLogger(__name__)

_executor = ThreadPoolExecutor(max_workers=2)


def _content_sha256(file_content: bytes) -> str:
    return hashlib.sha256(file_content).hexdigest()


def _find_duplicate_in_kb(db: Session, kb_id: int, content_hash: str) -> Document | None:
    return (
        db.query(Document)
        .filter(
            Document.knowledge_base_id == kb_id,
            Document.content_sha256 == content_hash,
            Document.status == "completed",
        )
        .first()
    )


def ingest_document_sync(doc_id: int, file_content: bytes) -> None:
    with tracer.start_as_current_span("ingest_document_background_task") as span:
        span.set_attribute("document_id", doc_id)
        db = SessionLocal()
        document: Document | None = None
        try:
            document = db.query(Document).filter(Document.id == doc_id).first()
            if not document:
                logger.error("Document not found for ingestion: %s", doc_id)
                span.set_attribute("error", True)
                return

            logger.info(
                "Starting ingestion for document: %s (ID: %s)",
                document.filename,
                doc_id,
            )
            span.set_attribute("document.filename", document.filename)

            document.status = "parsing"
            document.error_message = None
            db.add(document)
            db.commit()

            content = file_content
            if not content:
                storage = get_storage_client()
                loaded = storage.get_file(document.external_storage_ref)
                if not loaded:
                    raise ValueError(
                        "No file content for ingestion and storage read failed"
                    )
                content = loaded

            with tracer.start_as_current_span("parse_document"):
                mime_type = mimetypes.guess_type(document.filename)[0]
                if not mime_type:
                    mime_type = "application/octet-stream"
                span.set_attribute("document.mime_type", mime_type)

                parser = get_parser(mime_type)
                text_content = parser.parse(content)

            with tracer.start_as_current_span("extract_metadata"):
                metadata_extractor = get_metadata_extractor()
                extracted_metadata = metadata_extractor.extract(
                    content, document.filename, mime_type
                )

            document.mime_type = mime_type
            document.num_pages = extracted_metadata.get("num_pages")
            document.raw_content_size = len(content)
            document.content_sha256 = _content_sha256(content)
            document.embedding_model = embedding_service.model_name
            db.add(document)
            db.commit()

            duplicate = _find_duplicate_in_kb(
                db, document.knowledge_base_id, document.content_sha256
            )
            if duplicate and duplicate.id != document.id:
                document.status = "completed"
                document.chunk_count = duplicate.chunk_count
                document.embedding_model = duplicate.embedding_model
                document.error_message = None
                db.add(document)
                db.commit()
                logger.info(
                    "Document %s marked completed (duplicate of doc %s)",
                    doc_id,
                    duplicate.id,
                )
                return

            with tracer.start_as_current_span("chunk_document"):
                chunker = get_chunker()
                chunks_content = chunker.chunk(text_content)
                span.set_attribute("document.chunks_count", len(chunks_content))
                if not chunks_content:
                    raise ValueError("No text content extracted from document")

            document.status = "indexing"
            db.add(document)
            db.commit()

            db.query(DocumentChunk).filter(DocumentChunk.document_id == document.id).delete()
            db.commit()

            with tracer.start_as_current_span("create_chunks_and_embed"):
                embeddings = embedding_service.embed_batch(chunks_content)
                for index, (chunk_content, embedding) in enumerate(
                    zip(chunks_content, embeddings, strict=True)
                ):
                    db_chunk = DocumentChunk(
                        document_id=document.id,
                        chunk_index=index,
                        content=chunk_content,
                        source=document.filename,
                        page_number=extracted_metadata.get("page_number"),
                        section=extracted_metadata.get("section"),
                        embedding=embedding,
                    )
                    db.add(db_chunk)

                document.status = "completed"
                document.chunk_count = len(chunks_content)
                document.error_message = None
                db.add(document)
                db.commit()
                logger.info("Document %s ingestion completed successfully.", doc_id)

        except Exception as exc:
            logger.exception("Document ingestion failed for doc_id %s", doc_id)
            if document:
                document.status = "failed"
                document.error_message = str(exc)[:2000]
                db.add(document)
                db.commit()
            span.set_attribute("error", True)
            span.record_exception(exc)
        finally:
            db.close()


async def ingest_document_background_task(doc_id: int, file_content: bytes) -> None:
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(_executor, ingest_document_sync, doc_id, file_content)


class IngestionService:
    def __init__(self):
        self.storage_client = get_storage_client()

    async def upload_and_ingest_document(
        self,
        db: Session,
        user_id: int,
        kb_id: int,
        filename: str,
        file_content: bytes,
        *,
        schedule_ingestion: bool = True,
    ) -> Document:
        with tracer.start_as_current_span("upload_and_ingest_document") as span:
            span.set_attribute("user_id", user_id)
            span.set_attribute("kb_id", kb_id)
            span.set_attribute("filename", filename)

            duplicate = _find_duplicate_in_kb(db, kb_id, _content_sha256(file_content))
            if duplicate is not None:
                span.set_attribute("deduplicated", True)
                span.set_attribute("existing_document_id", duplicate.id)
                return duplicate

            object_key = build_document_object_key(kb_id, filename, uuid.uuid4().hex)
            mime_type = mimetypes.guess_type(filename)[0]
            storage_ref = self.storage_client.save_file(
                file_content,
                filename,
                object_key=object_key,
                content_type=mime_type,
            )

            new_document = Document(
                knowledge_base_id=kb_id,
                filename=filename,
                external_storage_ref=storage_ref,
                status="uploaded",
                raw_content_size=len(file_content),
                content_sha256=_content_sha256(file_content),
            )
            db.add(new_document)
            db.commit()
            db.refresh(new_document)
            span.set_attribute("document_id", new_document.id)
            logger.info("Document %s uploaded and awaiting ingestion.", new_document.id)

            if schedule_ingestion:
                await ingest_document_background_task(new_document.id, file_content)

            return new_document
