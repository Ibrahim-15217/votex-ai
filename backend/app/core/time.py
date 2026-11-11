"""Consistent UTC time handling for API output and audit hashing."""

from datetime import datetime, timezone


def utcnow() -> datetime:
    """Return the current time as a timezone-aware UTC datetime."""

    return datetime.now(timezone.utc)


def to_iso_utc(value: datetime | None) -> str | None:
    """Serialise a datetime as an ISO 8601 UTC string with a trailing Z."""

    if value is None:
        return None
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def canonical_timestamp(value: datetime) -> str:
    """Return a stable timestamp string used inside audit hashes.

    SQLite returns naive datetimes while insertion is aware. Normalising to
    naive UTC keeps the recomputed hash identical across database backends.
    """

    if value.tzinfo is not None:
        value = value.astimezone(timezone.utc).replace(tzinfo=None)
    return value.isoformat(timespec="microseconds")
