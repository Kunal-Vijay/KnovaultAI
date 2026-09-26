from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from app.core.config import settings
from app.db.url import (
    database_url_with_ssl_query,
    normalize_database_url,
    sqlalchemy_connect_args,
)

SQLALCHEMY_DATABASE_URL = database_url_with_ssl_query(
    normalize_database_url(settings.DATABASE_URL)
)

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args=sqlalchemy_connect_args(SQLALCHEMY_DATABASE_URL),
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Import all models to ensure they are registered with SQLAlchemy Base.metadata
from app import models
