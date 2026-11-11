"""Evidence validation, hashing, storage and access logging."""

from __future__ import annotations

import re
from hashlib import sha256
from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status as http_status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.time import utcnow
from app.db.models import Evidence, Incident, User
from app.services.audit import record_audit
from app.services.correlation import sync_incident_indicators
from app.services.incidents import add_event, humanise

ALLOWED_TYPES: dict[str, set[str]] = {
    "image/png": {".png"},
    "image/jpeg": {".jpg", ".jpeg"},
    "image/webp": {".webp"},
    "application/pdf": {".pdf"},
    "text/plain": {".txt"},
    "message/rfc822": {".eml"},
}

ALLOWED_EXTENSIONS = {ext for extensions in ALLOWED_TYPES.values() for ext in extensions}
CHUNK_SIZE = 1024 * 1024


def _safe_original_name(filename: str | None) -> str:
    name = Path(filename or "evidence").name
    name = re.sub(r"[\x00-\x1f\x7f]", "", name).strip()
    if not name or name in {".", ".."}:
        name = "evidence"
    return name[:180]


def _magic_matches(extension: str, head: bytes) -> bool:
    if extension == ".png":
        return head.startswith(b"\x89PNG\r\n\x1a\n")
    if extension in {".jpg", ".jpeg"}:
        return head.startswith(b"\xff\xd8\xff")
    if extension == ".webp":
        return len(head) >= 12 and head[:4] == b"RIFF" and head[8:12] == b"WEBP"
    if extension == ".pdf":
        return head.startswith(b"%PDF")
    # Plain text and email files have no reliable magic signature.
    return True


def _target_path(incident: Incident, stored_filename: str) -> Path:
    base = Path(settings.evidence_dir).resolve()
    target = (base / incident.id / stored_filename).resolve()
    if base != target and base not in target.parents:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST, detail="Invalid evidence path."
        )
    return target


def store_evidence(db: Session, user: User, incident: Incident, upload: UploadFile) -> Evidence:
    """Validate, hash and persist one evidence file."""

    content_type = (upload.content_type or "").lower().split(";")[0].strip()
    if content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=http_status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Unsupported file type. Upload PNG, JPEG, WebP, PDF, TXT or EML.",
        )

    original_name = _safe_original_name(upload.filename)
    extension = Path(original_name).suffix.lower()
    if extension not in ALLOWED_TYPES[content_type]:
        raise HTTPException(
            status_code=http_status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="The file extension does not match the declared content type.",
        )

    max_bytes = settings.max_evidence_mb * 1024 * 1024
    hasher = sha256()
    total = 0
    stored_filename = f"{uuid4().hex}{extension}"
    target = _target_path(incident, stored_filename)
    target.parent.mkdir(parents=True, exist_ok=True)

    first_chunk = upload.file.read(CHUNK_SIZE)
    if not first_chunk:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST, detail="The uploaded file is empty."
        )
    if not _magic_matches(extension, first_chunk[:16]):
        raise HTTPException(
            status_code=http_status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="The file content does not match its declared type.",
        )

    try:
        with target.open("wb") as handle:
            chunk = first_chunk
            while chunk:
                total += len(chunk)
                if total > max_bytes:
                    raise HTTPException(
                        status_code=http_status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail=f"Evidence must be {settings.max_evidence_mb} MB or smaller.",
                    )
                hasher.update(chunk)
                handle.write(chunk)
                chunk = upload.file.read(CHUNK_SIZE)
    except HTTPException:
        target.unlink(missing_ok=True)
        raise

    digest = hasher.hexdigest()
    evidence = Evidence(
        incident_id=incident.id,
        organisation_id=user.organisation_id,
        uploaded_by_id=user.id,
        original_filename=original_name,
        stored_filename=stored_filename,
        content_type=content_type,
        size_bytes=total,
        sha256=digest,
        created_at=utcnow(),
    )
    db.add(evidence)
    add_event(
        db,
        incident,
        user,
        "evidence_added",
        f"Evidence uploaded: {original_name} ({total:,} bytes).",
        {"filename": original_name, "sha256": digest, "size_bytes": total},
    )
    record_audit(
        db,
        action="evidence.uploaded",
        actor_id=user.id,
        organisation_id=user.organisation_id,
        resource_type="evidence",
        resource_id=evidence.id,
        detail={
            "incident_reference": incident.reference,
            "filename": original_name,
            "content_type": content_type,
            "size_bytes": total,
            "sha256": digest,
        },
    )
    db.commit()
    db.refresh(evidence)

    # Evidence hashes and text/EML bodies are valuable indicators. Refresh the
    # relationship so the newly stored file is included in this pass.
    try:
        db.expire(incident, ["evidence"])
        sync_incident_indicators(db, incident, user)
        db.refresh(evidence)
    except Exception:
        db.rollback()
    return evidence


def find_evidence(incident: Incident, evidence_id: str) -> Evidence:
    """Find evidence attached to an already-authorised incident."""

    for item in incident.evidence:
        if item.id == evidence_id:
            return item
    raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail="Evidence not found.")


def evidence_path(evidence: Evidence) -> Path:
    """Resolve and validate the stored path for an evidence file."""

    base = Path(settings.evidence_dir).resolve()
    target = (base / evidence.incident_id / evidence.stored_filename).resolve()
    if base not in target.parents or not target.is_file():
        raise HTTPException(
            status_code=http_status.HTTP_410_GONE,
            detail="The evidence file is missing from storage.",
        )
    return target


def record_access(
    db: Session, user: User, incident: Incident, evidence: Evidence
) -> None:
    """Record an evidence download in the timeline and audit chain."""

    add_event(
        db,
        incident,
        user,
        "evidence_accessed",
        f"Evidence accessed: {evidence.original_filename}.",
        {"evidence_id": evidence.id, "sha256": evidence.sha256},
    )
    record_audit(
        db,
        action="evidence.downloaded",
        actor_id=user.id,
        organisation_id=user.organisation_id,
        resource_type="evidence",
        resource_id=evidence.id,
        detail={
            "incident_reference": incident.reference,
            "filename": evidence.original_filename,
            "sha256": evidence.sha256,
        },
    )
    db.commit()


def describe_evidence(evidence: Evidence) -> dict:
    """Small helper used by tests and diagnostics."""

    return {
        "id": evidence.id,
        "filename": evidence.original_filename,
        "sha256": evidence.sha256,
        "size_bytes": evidence.size_bytes,
        "uploaded": humanise(evidence.content_type),
    }
