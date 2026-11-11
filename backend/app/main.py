"""Votex AI FastAPI application.

Phase 1 mounts the secure workflow spine: JWT authentication, tenant-scoped
incidents, evidence hashing and an append-only audit chain. The hybrid AI
engine arrives in Phase 2.
"""

from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.db.init_db import init_db
from app.db.session import SessionLocal
from app.seed import seed_demo_data
from app.services.analysis import backfill_missing_analyses
from app.services.correlation import backfill_indicators


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """Create tables, seed the synthetic demo tenant and backfill analyses."""

    init_db()
    if settings.auto_seed:
        seed_demo_data()
    with SessionLocal() as db:
        backfill_missing_analyses(db)
        backfill_indicators(db)
    yield


app = FastAPI(
    title="Votex AI API",
    summary="Electoral cybersecurity intelligence and incident coordination",
    description=(
        "Prototype API for the #AI4Elections Hackathon 2026–2027, Track 4. "
        "Synthetic data only; not affiliated with INEC or any partner."
    ),
    version=settings.app_version,
    docs_url="/api/docs",
    redoc_url=None,
    openapi_url="/api/openapi.json",
    contact={"name": "Votex AI contributors"},
    license_info={"name": "MIT"},
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/", tags=["meta"], summary="Service identity")
def root() -> dict:
    """Return service identity without exposing configuration secrets."""

    return {
        "service": "votex-ai-api",
        "version": settings.app_version,
        "docs": "/api/docs",
        "health": "/api/v1/health",
        "phase": "hybrid-ai-engine",
    }
