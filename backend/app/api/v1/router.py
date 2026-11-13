"""Aggregate all versioned API routers."""

from fastapi import APIRouter

from app.api.v1 import (
    audit,
    auth,
    demo,
    evidence,
    health,
    incidents,
    intelligence,
    resilience,
    users,
)

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(demo.router)
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(incidents.router)
api_router.include_router(evidence.router)
api_router.include_router(intelligence.router)
api_router.include_router(resilience.router)
api_router.include_router(audit.router)
