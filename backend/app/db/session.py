"""Database engine and session management.

PostgreSQL is the target. SQLite is supported for local checks and tests, with
foreign-key enforcement enabled explicitly.
"""

from collections.abc import Generator
from pathlib import Path

from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings

_is_sqlite = settings.database_url.startswith("sqlite")

if _is_sqlite:
    # Make relative SQLite paths resolve from the backend directory regardless
    # of where the process was started.
    if ":///" in settings.database_url and not settings.database_url.startswith("sqlite:////"):
        raw_path = settings.database_url.split(":///", 1)[1]
        if raw_path and raw_path != ":memory:":
            resolved = (Path(__file__).resolve().parents[2] / raw_path).resolve()
            database_url = f"sqlite:///{resolved.as_posix()}"
        else:
            database_url = settings.database_url
    else:
        database_url = settings.database_url
    connect_args = {"check_same_thread": False}
else:
    database_url = settings.database_url
    connect_args = {}

engine = create_engine(database_url, connect_args=connect_args, pool_pre_ping=True)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


if _is_sqlite:

    @event.listens_for(engine, "connect")
    def _enable_sqlite_foreign_keys(dbapi_connection, _connection_record) -> None:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency that yields a database session."""

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
