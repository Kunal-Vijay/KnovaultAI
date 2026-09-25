from fastapi import APIRouter, Depends, HTTPException, status
from app.db.session import get_db
from sqlalchemy.orm import Session
from sqlalchemy import text

router = APIRouter()

@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    return {"status": "ok", "message": "FastAPI service is healthy"}

@router.get("/ready", status_code=status.HTTP_200_OK)
async def readiness_check(db: Session = Depends(get_db)):
    try:
        # Attempt to execute a simple query to check DB connection
        db.execute(text("SELECT 1"))
        return {"status": "ok", "message": "FastAPI service and database are ready"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Database not ready: {e}")
