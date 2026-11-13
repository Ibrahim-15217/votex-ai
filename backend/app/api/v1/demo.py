"""Public, synthetic-only telemetry for the sign-in screen.

The sign-in screen shows a small set of counts before a session exists. Those
counts must come from the same database as the console, but they must never
expose another organisation's records. This router is therefore hard-scoped to
the seeded synthetic demo tenant and returns zeroes when that tenant is absent.
"""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models import AuditLog, Incident, Indicator, Organisation
from app.db.session import get_db

router = APIRouter(prefix="/demo", tags=["demo"])
DbSession = Annotated[Session, Depends(get_db)]

DEMO_ORGANISATION_SLUG = "votex-demo-authority"

_EMPTY_TELEMETRY = {
    "synthetic": True,
    "incidents": 0,
    "indicators": 0,
    "audit_entries": 0,
}


@router.get("/telemetry", summary="Synthetic demo counts for the sign-in screen")
def demo_telemetry(db: DbSession) -> dict:
    """Return counts for the synthetic demo tenant only."""

    organisation_id = db.scalar(
        select(Organisation.id).where(Organisation.slug == DEMO_ORGANISATION_SLUG)
    )
    if organisation_id is None:
        return dict(_EMPTY_TELEMETRY)

    incidents = db.scalar(
        select(func.count())
        .select_from(Incident)
        .where(Incident.organisation_id == organisation_id)
    )
    indicators = db.scalar(
        select(func.count())
        .select_from(Indicator)
        .where(Indicator.organisation_id == organisation_id)
    )
    audit_entries = db.scalar(
        select(func.count())
        .select_from(AuditLog)
        .where(AuditLog.organisation_id == organisation_id)
    )

    return {
        "synthetic": True,
        "incidents": int(incidents or 0),
        "indicators": int(indicators or 0),
        "audit_entries": int(audit_entries or 0),
    }
