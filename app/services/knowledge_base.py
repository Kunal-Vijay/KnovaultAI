from sqlalchemy.orm import Session
from app.models.knowledge_base import KnowledgeBase
from app.schemas.knowledge_base import KnowledgeBaseCreate

def get_knowledge_base(db: Session, kb_id: int):
    return db.query(KnowledgeBase).filter(KnowledgeBase.id == kb_id).first()

def get_knowledge_bases_for_owner(db: Session, owner_id: int, skip: int = 0, limit: int = 100):
    return db.query(KnowledgeBase).filter(KnowledgeBase.owner_id == owner_id).offset(skip).limit(limit).all()

def create_knowledge_base(db: Session, kb: KnowledgeBaseCreate, owner_id: int):
    db_kb = KnowledgeBase(**kb.dict(), owner_id=owner_id)
    db.add(db_kb)
    db.commit()
    db.refresh(db_kb)
    return db_kb
