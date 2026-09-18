
from pathlib import Path

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings


class Base(DeclarativeBase):
    pass


def _ensure_sqlite_directory() -> None:
    if not settings.database_url.startswith("sqlite:///"):
        return

    database_path = settings.database_url.removeprefix("sqlite:///")
    if database_path == ":memory:":
        return
    Path(database_path).parent.mkdir(parents=True, exist_ok=True)


_ensure_sqlite_directory()
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False}
    if settings.database_url.startswith("sqlite")
    else {},
)


def initialize_database() -> None:
    from app.db import models  # noqa: F401

    Base.metadata.create_all(bind=engine)
    if engine.dialect.name == "sqlite":
        _upgrade_existing_sqlite_schema()


def _upgrade_existing_sqlite_schema() -> None:
    inspector = inspect(engine)
    if not inspector.has_table("scholarships"):
        return
    existing_columns = {
        column["name"] for column in inspector.get_columns("scholarships")
    }
    additions = {
        "amount": "FLOAT",
        "currency": "VARCHAR(16)",
        "source_status": "VARCHAR(32)",
        "status_derived": "BOOLEAN NOT NULL DEFAULT 0",
        "data_quality": "VARCHAR(32) NOT NULL DEFAULT 'needs_review'",
        "quality_issues": "JSON",
        "fingerprint": "VARCHAR(128)",
        "eligibility_evidence": "JSON",
        "legacy_metadata": "JSON",
        "source_record_id": "VARCHAR(255)",
    }
    with engine.begin() as connection:
        for column, definition in additions.items():
            if column not in existing_columns:
                connection.execute(text(f"ALTER TABLE scholarships ADD COLUMN {column} {definition}"))