from datetime import datetime, timedelta
from typing import Optional

import bcrypt
from jose import JWTError, jwt

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.user import User
from app.schemas.user import TokenData
from app.db.session import get_db # Import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="v1/token")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8"),
    )


def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    from app.services.user import get_user_by_username

    user = get_user_by_username(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

# This function can be used for endpoints that need an active user
async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return current_user


def can_upload_from_token_payload(payload: dict) -> bool:
    """JWT claim can_upload; omitted defaults to True for backward compatibility."""
    value = payload.get("can_upload", True)
    if isinstance(value, bool):
        return value
    return True


def decode_access_token_payload(token: str) -> dict:
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])


async def require_can_upload(token: str = Depends(oauth2_scheme)) -> None:
    try:
        payload = decode_access_token_payload(token)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not can_upload_from_token_payload(payload):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Upload not allowed for demo sessions",
        )
