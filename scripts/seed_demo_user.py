#!/usr/bin/env python3
"""Create or update the shared demo user (run once per environment after migrations)."""

import os
import sys

from sqlalchemy.orm import Session

# Allow running from repo root: python scripts/seed_demo_user.py
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.config import settings
from app.core.security import get_password_hash
from app.db.session import SessionLocal
from app.models.user import User
from app.services.user import get_user_by_username


def seed_demo_user(db: Session) -> User:
    username = settings.DEMO_USERNAME
    # Must pass Pydantic EmailStr on GET /users/me (.local is rejected)
    email = os.environ.get("DEMO_EMAIL", f"{username}@example.com")
    password = os.environ.get("DEMO_PASSWORD")
    if not password:
        print("Set DEMO_PASSWORD in the environment before running this script.", file=sys.stderr)
        sys.exit(1)

    existing = get_user_by_username(db, username=username)
    if existing:
        existing.email = email
        existing.hashed_password = get_password_hash(password)
        existing.is_active = True
        db.commit()
        db.refresh(existing)
        print(f"Updated demo user '{username}' (id={existing.id}).")
        return existing

    user = User(
        username=username,
        email=email,
        hashed_password=get_password_hash(password),
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    print(f"Created demo user '{username}' (id={user.id}).")
    return user


def main() -> None:
    db = SessionLocal()
    try:
        seed_demo_user(db)
    finally:
        db.close()


if __name__ == "__main__":
    main()
