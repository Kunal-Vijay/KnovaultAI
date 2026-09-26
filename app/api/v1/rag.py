from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.llm.errors import LLMError, ModelAuthenticationError, ModelRateLimitError
from app.core.security import get_current_active_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.rag import RAGRequest, RAGResponse
from app.services.knowledge_base import get_knowledge_base
from app.services.rag import rag_service

router = APIRouter()


@router.post("/rag", response_model=RAGResponse, status_code=status.HTTP_200_OK)
async def get_rag_answer(
    request: RAGRequest,
    user_id: int,
    http_request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform RAG for this user",
        )
    db_kb = get_knowledge_base(db, kb_id=request.knowledge_base_id)
    if db_kb is None or db_kb.owner_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Knowledge Base not found for this user or unauthorized",
        )

    request_id = http_request.headers.get("x-request-id")

    try:
        return await rag_service.get_answer(
            db,
            request,
            user_id=user_id,
            request_id=request_id,
        )
    except ModelAuthenticationError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    except ModelRateLimitError as exc:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=str(exc)) from exc
    except LLMError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc
