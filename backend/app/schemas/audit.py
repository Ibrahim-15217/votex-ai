"""Audit log schemas."""

from pydantic import BaseModel

from app.schemas.common import ORMModel, UTCDateTime


class AuditEntryOut(ORMModel):
    id: int
    organisation_id: int | None = None
    actor_id: int | None = None
    actor_email: str | None = None
    action: str
    resource_type: str | None = None
    resource_id: str | None = None
    detail: dict
    created_at: UTCDateTime
    prev_hash: str
    entry_hash: str


class AuditPage(BaseModel):
    items: list[AuditEntryOut]
    total: int
    page: int
    page_size: int


class AuditVerifyResult(BaseModel):
    valid: bool
    entries_checked: int
    first_invalid_id: int | None = None
    message: str
    latest_hash: str | None = None
    checked_at: UTCDateTime
