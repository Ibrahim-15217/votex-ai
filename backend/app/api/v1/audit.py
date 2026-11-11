"""Audit chain browsing and verification."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.api.deps import AnalystUser
from app.core.time import utcnow
from app.db.models import AuditLog
from app.db.session import get_db
from app.schemas.audit import AuditEntryOut, AuditPage, AuditVerifyResult
from app.services.audit import verify_audit_chain

router = APIRouter(prefix="/audit", tags=["audit"])
DbSession = Annotated[Session, Depends(get_db)]


@router.get("", response_model=AuditPage, summary="Browse the audit chain")
def list_audit(
    current_user: AnalystUser,
    db: DbSession,
    action: Annotated[str | None, Query(max_length=80)] = None,
    page: Annotated[int, Query(ge=1, le=10_000)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 50,
) -> AuditPage:
    """Return the caller's organisation audit entries, newest first."""

    conditions = [AuditLog.organisation_id == current_user.organisation_id]
    if action:
        conditions.append(AuditLog.action == action)

    total = db.scalar(select(func.count()).select_from(AuditLog).where(*conditions)) or 0
    items = db.scalars(
        select(AuditLog)
        .options(selectinload(AuditLog.actor))
        .where(*conditions)
        .order_by(AuditLog.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()

    return AuditPage(items=list(items), total=total, page=page, page_size=page_size)


@router.get("/verify", response_model=AuditVerifyResult, summary="Verify the hash chain")
def verify_audit(current_user: AnalystUser, db: DbSession) -> AuditVerifyResult:
    """Recompute the entire audit chain and report the first broken entry."""

    result = verify_audit_chain(db)
    return AuditVerifyResult(
        valid=result.valid,
        entries_checked=result.entries_checked,
        first_invalid_id=result.first_invalid_id,
        message=result.message,
        latest_hash=result.latest_hash,
        checked_at=utcnow(),
    )
