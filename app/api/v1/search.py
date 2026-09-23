from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.schemas.search import SearchRequest, SearchResponse
from app.services.search import semantic_search_service
from app.services.knowledge_base import get_knowledge_base

router = APIRouter()

@router.post("/search", response_model=SearchResponse, status_code=status.HTTP_200_OK)
def search_knowledge_base(
    request: SearchRequest,
    user_id: int, # Assuming user_id is passed for context/authorization
    db: Session = Depends(get_db)
):
    # Verify knowledge base ownership or access
    db_kb = get_knowledge_base(db, kb_id=request.knowledge_base_id)
    if db_kb is None or db_kb.owner_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Knowledge Base not found for this user or unauthorized")
    
    results = semantic_search_service.search(db, request)
    return SearchResponse(results=results)
