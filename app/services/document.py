from sqlalchemy.orm import Session
from app.models.document import Document
from app.schemas.document import DocumentCreate

def get_document(db: Session, doc_id: int):
    return db.query(Document).filter(Document.id == doc_id).first()

def get_documents_for_knowledge_base(db: Session, kb_id: int, skip: int = 0, limit: int = 100):
    return db.query(Document).filter(Document.knowledge_base_id == kb_id).offset(skip).limit(limit).all()

def create_document(db: Session, doc: DocumentCreate, kb_id: int):
    db_doc = Document(**doc.dict(), knowledge_base_id=kb_id)
    db.add(db_doc)
    db.commit()
    db.refresh(db_doc)
    return db_doc
