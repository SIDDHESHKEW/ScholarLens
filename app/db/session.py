
from sqlalchemy.orm import Session, sessionmaker

from app.db.base import engine

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db_session() -> Session:
    return SessionLocal()