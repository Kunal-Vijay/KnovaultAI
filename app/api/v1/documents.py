from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.user import User
from app.schemas.document import Document, DocumentCreate, DocumentUploadRequest
from app.services import document as doc_service
from app.services import knowledge_base as kb_service
from app.services.ingestion import IngestionService, ingest_document_sync
from app.core.security import get_current_active_user, require_can_upload

router = APIRouter()

@router.post("/users/{user_id}/knowledge_bases/{kb_id}/documents/", response_model=Document, status_code=status.HTTP_201_CREATED)
def create_doc_for_kb(
    user_id: int,
    kb_id: int,
    doc_create: DocumentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    _: None = Depends(require_can_upload),
):
    if current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to create document for this user")
    db_kb = kb_service.get_knowledge_base(db, kb_id=kb_id)
    if db_kb is None or db_kb.owner_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Knowledge Base not found for this user")
    return doc_service.create_document(db=db, doc=doc_create, kb_id=kb_id)

@router.get("/users/{user_id}/knowledge_bases/{kb_id}/documents/", response_model=List[Document])
def read_docs_for_kb(
    user_id: int,
    kb_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view documents for this user")
    db_kb = kb_service.get_knowledge_base(db, kb_id=kb_id)
    if db_kb is None or db_kb.owner_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Knowledge Base not found for this user")
    docs = doc_service.get_documents_for_knowledge_base(db, kb_id=kb_id, skip=skip, limit=limit)
    return docs

@router.get("/users/{user_id}/knowledge_bases/{kb_id}/documents/{doc_id}", response_model=Document)
def read_doc_for_kb(
    user_id: int,
    kb_id: int,
    doc_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view document for this user")
    db_kb = kb_service.get_knowledge_base(db, kb_id=kb_id)
    if db_kb is None or db_kb.owner_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Knowledge Base not found for this user")
    db_doc = doc_service.get_document(db, doc_id=doc_id)
    if db_doc is None or db_doc.knowledge_base_id != kb_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found in this Knowledge Base")
    return db_doc

@router.post("/users/{user_id}/knowledge_bases/{kb_id}/documents/upload", response_model=Document, status_code=status.HTTP_202_ACCEPTED)
async def upload_document_for_kb(
    user_id: int,
    kb_id: int,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    _: None = Depends(require_can_upload),
):
    if current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to upload document for this user")
    db_kb = kb_service.get_knowledge_base(db, kb_id=kb_id)
    if db_kb is None or db_kb.owner_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Knowledge Base not found for this user")

    # Read file content asynchronously
    file_content = await file.read()

    ingestion_service = IngestionService()
    new_document = await ingestion_service.upload_and_ingest_document(
        db=db,
        user_id=user_id,
        kb_id=kb_id,
        filename=file.filename,
        file_content=file_content,
        schedule_ingestion=False,
    )
    if new_document.status == "uploaded":
        background_tasks.add_task(ingest_document_sync, new_document.id, file_content)
    return new_document
