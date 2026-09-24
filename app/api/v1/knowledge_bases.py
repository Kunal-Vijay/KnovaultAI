from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.user import User
from app.schemas.knowledge_base import KnowledgeBase, KnowledgeBaseCreate
from app.services import knowledge_base as kb_service
from app.services import user as user_service
from app.core.security import get_current_active_user

router = APIRouter()

@router.post("/users/{user_id}/knowledge_bases/", response_model=KnowledgeBase, status_code=status.HTTP_201_CREATED)
def create_kb_for_user(
    user_id: int,
    kb: KnowledgeBaseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to create knowledge base for this user")
    db_user = user_service.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return kb_service.create_knowledge_base(db=db, kb=kb, owner_id=user_id)

@router.get("/users/{user_id}/knowledge_bases/", response_model=List[KnowledgeBase])
def read_kbs_for_user(
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view knowledge bases for this user")
    db_user = user_service.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    kbs = kb_service.get_knowledge_bases_for_owner(db, owner_id=user_id, skip=skip, limit=limit)
    return kbs

@router.get("/users/{user_id}/knowledge_bases/{kb_id}", response_model=KnowledgeBase)
def read_kb_for_user(
    user_id: int,
    kb_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view knowledge base for this user")
    db_kb = kb_service.get_knowledge_base(db, kb_id=kb_id)
    if db_kb is None or db_kb.owner_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Knowledge Base not found for this user")
    return db_kb
