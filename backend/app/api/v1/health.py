"""Health and readiness endpoints.

Readiness checks the database connection and reports whether the hybrid AI
engine can load its trained artefact. Model loading is lazy, so the API can
start before training has run; this endpoint makes that state visible.
"""

from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter
from sqlalchemy import text

from app.ai.ml import load_model
from app.core.config import settings
from app.db.session import engine

router = APIRouter(tags=["health"])


def _database_status() -> str:
    """Return ``ok`` when a simple query succeeds."""

    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return "ok"
    except Exception:  # pragma: no cover - defensive readiness path
        return "unavailable"


def _ai_status() -> str:
    """Report whether the trained model artefact is present and loadable."""

    bundle = load_model()
    if bundle is None:
        return "model-unavailable"
    return "ok" if bundle.get("pipeline") is not None else "model-invalid"


@router.get("/health", summary="Service health and build metadata")
def health() -> dict:
    """Return a lightweight, non-sensitive health response."""

    return {
        "status": "ok",
        "service": "votex-ai-api",
        "version": settings.app_version,
        "environment": settings.environment,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "checks": {
            "api": "ok",
            "database": _database_status(),
            "evidence_store": "ok" if Path(settings.evidence_dir).exists() else "not-created",
            "ai_engine": _ai_status(),
        },
    }


@router.get("/ready", summary="Readiness probe")
def ready() -> dict:
    """Readiness probe used by orchestration and the demo pre-flight check."""

    return {"ready": True, "phase": "resilience-and-simulation"}
