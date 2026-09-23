from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.schemas.document import Document, DocumentCreate
from app.services import document as doc_service
from app.services import knowledge_base as kb_service

router = APIRouter()

@router.post("/users/{user_id}/knowledge_bases/{kb_id}/documents/", response_model=Document, status_code=status.HTTP_201_CREATED)
def create_doc_for_kb(
    user_id: int,
    kb_id: int,
    doc: DocumentCreate,
    db: Session = Depends(get_db)
):
    db_kb = kb_service.get_knowledge_base(db, kb_id=kb_id)
    if db_kb is None or db_kb.owner_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Knowledge Base not found for this user")
    return doc_service.create_document(db=db, doc=doc, kb_id=kb_id)

@router.get("/users/{user_id}/knowledge_bases/{kb_id}/documents/", response_model=List[Document])
def read_docs_for_kb(
    user_id: int,
    kb_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
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
    db: Session = Depends(get_db)
):
    db_kb = kb_service.get_knowledge_base(db, kb_id=kb_id)
    if db_kb is None or db_kb.owner_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Knowledge Base not found for this user")
    db_doc = doc_service.get_document(db, doc_id=doc_id)
    if db_doc is None or db_doc.knowledge_base_id != kb_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found in this Knowledge Base")
    return db_doc
