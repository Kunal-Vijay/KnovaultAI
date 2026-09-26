from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.schemas.user import User, UserCreate
from app.services import user as user_service
from app.core.security import get_current_active_user # Import for authorization
from app.core.config import settings

router = APIRouter()

@router.post("/users/", response_model=User, status_code=status.HTTP_201_CREATED)
def create_new_user(user: UserCreate, db: Session = Depends(get_db)):
    if not settings.ALLOW_PUBLIC_REGISTRATION:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Public registration is disabled",
        )
    db_user = user_service.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    db_user = user_service.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered")
    return user_service.create_user(db=db, user=user)

@router.get("/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user

@router.get("/users/{user_id}", response_model=User)
def read_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    # Only allow a user to see their own profile or if an admin role was implemented.
    # For now, only the user themselves can view their user_id.
    if current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this user's profile")
    db_user = user_service.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return db_user
