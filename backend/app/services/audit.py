"""Append-only, SHA-256 hash-chained audit log.

Each entry hashes the previous entry's hash plus a canonical representation of
the new entry. Any edit, deletion or reordering breaks verification.
"""

from dataclasses import dataclass
from hashlib import sha256
from json import dumps, loads
from threading import Lock

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.time import canonical_timestamp, utcnow
from app.db.models import AuditLog

GENESIS_HASH = "0" * 64
_audit_lock = Lock()


@dataclass
class AuditVerification:
    valid: bool
    entries_checked: int
    first_invalid_id: int | None
    message: str
    latest_hash: str | None


def _canonical_json(value: dict) -> str:
    return dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _entry_payload(entry: AuditLog) -> dict:
    return {
        "id": entry.id,
        "organisation_id": entry.organisation_id,
        "actor_id": entry.actor_id,
        "action": entry.action,
        "resource_type": entry.resource_type,
        "resource_id": entry.resource_id,
        "detail": loads(entry.detail_json or "{}"),
        "created_at": canonical_timestamp(entry.created_at),
        "prev_hash": entry.prev_hash,
    }


def _hash_entry(entry: AuditLog) -> str:
    return sha256(_canonical_json(_entry_payload(entry)).encode("utf-8")).hexdigest()


def record_audit(
    db: Session,
    *,
    action: str,
    actor_id: int | None = None,
    organisation_id: int | None = None,
    resource_type: str | None = None,
    resource_id: str | None = None,
    detail: dict | None = None,
) -> AuditLog:
    """Append one audit entry inside the caller's transaction.

    The caller must commit. A process-level lock serialises appends in the MVP;
    production would use a dedicated audit writer or database advisory lock.
    """

    detail = detail or {}
    with _audit_lock:
        previous = db.scalars(select(AuditLog).order_by(AuditLog.id.desc()).limit(1)).first()
        prev_hash = previous.entry_hash if previous else GENESIS_HASH
        created_at = utcnow()
        entry = AuditLog(
            organisation_id=organisation_id,
            actor_id=actor_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            detail_json=_canonical_json(detail),
            created_at=created_at,
            prev_hash=prev_hash,
            entry_hash="",
        )
        db.add(entry)
        db.flush()  # assign the sequential id used in the hash
        entry.entry_hash = _hash_entry(entry)
        db.flush()
        return entry


def verify_audit_chain(db: Session) -> AuditVerification:
    """Recompute the full chain and report the first broken entry."""

    entries = db.scalars(select(AuditLog).order_by(AuditLog.id)).all()
    previous_hash = GENESIS_HASH
    latest_hash: str | None = None

    for index, entry in enumerate(entries, start=1):
        if entry.prev_hash != previous_hash:
            return AuditVerification(
                valid=False,
                entries_checked=index,
                first_invalid_id=entry.id,
                message=(
                    f"Entry {entry.id} does not link to the previous entry. "
                    "An earlier entry may have been edited or removed."
                ),
                latest_hash=latest_hash,
            )

        expected = _hash_entry(entry)
        if expected != entry.entry_hash:
            return AuditVerification(
                valid=False,
                entries_checked=index,
                first_invalid_id=entry.id,
                message=(
                    f"Entry {entry.id} failed hash verification. "
                    "Its content no longer matches the recorded hash."
                ),
                latest_hash=latest_hash,
            )

        previous_hash = entry.entry_hash
        latest_hash = entry.entry_hash

    return AuditVerification(
        valid=True,
        entries_checked=len(entries),
        first_invalid_id=None,
        message=(
            "Audit chain verified. Every entry links to its predecessor."
            if entries
            else "Audit chain is empty."
        ),
        latest_hash=latest_hash,
    )
