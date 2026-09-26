from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from app.db.session import get_db
from app.schemas.user import Token
from app.services import user as user_service
from app.core.security import verify_password, create_access_token
from app.core.config import settings

router = APIRouter()

@router.post("/token", response_model=Token, tags=["Authentication"])
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = user_service.get_user_by_username(db, username=form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "user_id": user.id, "can_upload": True},
        expires_delta=access_token_expires,
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/auth/demo", response_model=Token, tags=["Authentication"])
async def login_as_demo(db: Session = Depends(get_db)):
    if not settings.DEMO_LOGIN_ENABLED:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Demo login is not enabled")
    user = user_service.get_user_by_username(db, username=settings.DEMO_USERNAME)
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Demo user is not configured. Run scripts/seed_demo_user.py.",
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "user_id": user.id, "can_upload": False},
        expires_delta=access_token_expires,
    )
    return {"access_token": access_token, "token_type": "bearer"}
