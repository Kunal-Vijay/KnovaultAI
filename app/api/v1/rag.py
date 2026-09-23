from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.rag import RAGRequest, RAGResponse
from app.services.rag import rag_service
from app.services.knowledge_base import get_knowledge_base

router = APIRouter()

@router.post("/rag", response_model=RAGResponse, status_code=status.HTTP_200_OK)
def get_rag_answer(
    request: RAGRequest,
    user_id: int, # Assuming user_id is passed for context/authorization
    db: Session = Depends(get_db)
):
    # Verify knowledge base ownership or access
    db_kb = get_knowledge_base(db, kb_id=request.knowledge_base_id)
    if db_kb is None or db_kb.owner_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Knowledge Base not found for this user or unauthorized")
    
    response = rag_service.get_answer(db, request)
    return response
