from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.user import User
from app.schemas.search import SearchRequest, SearchResponse
from app.services.search import hybrid_search_service # Use the new hybrid search service
from app.services.knowledge_base import get_knowledge_base
from app.core.security import get_current_active_user # Import for authorization

router = APIRouter()

@router.post("/search", response_model=SearchResponse, status_code=status.HTTP_200_OK)
def search_knowledge_base(
    request: SearchRequest,
    user_id: int, # Assuming user_id is passed for context/authorization
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to search for this user")
    # Verify knowledge base ownership or access
    db_kb = get_knowledge_base(db, kb_id=request.knowledge_base_id)
    if db_kb is None or db_kb.owner_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Knowledge Base not found for this user or unauthorized")
    
    results = hybrid_search_service.search(db, request)
    return SearchResponse(results=results)
