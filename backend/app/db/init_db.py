"""Create database tables and the evidence directory.

The hackathon prototype uses ``create_all`` for speed and reproducibility.
Alembic migrations are the post-hackathon path for schema evolution.
"""

from pathlib import Path

from app.core.config import settings
from app.db import models  # noqa: F401  (import registers the models)
from app.db.base import Base
from app.db.session import engine


def init_db() -> None:
    """Create all tables and ensure evidence storage exists."""

    Base.metadata.create_all(bind=engine)
    Path(settings.evidence_dir).mkdir(parents=True, exist_ok=True)
